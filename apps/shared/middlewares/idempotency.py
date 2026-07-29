import json
import logging
import re
import uuid

from django.core.cache import cache
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

IDEMPOTENCY_TTL = 24 * 60 * 60  # 24 hours
IDEMPOTENCY_METHODS = {"POST"}
IDEMPOTENCY_PATHS = ["/api/v1/payments"]


class IdempotencyMiddleware(MiddlewareMixin):
    """
    Prevents duplicate payment processing on network retries.

    Flow:
    1. Client sends unique UUID v4 in X-Idempotency-Key header
    2. Middleware checks Redis for this key
    3. Found  → return cached response immediately (no DB touch)
    4. Not found → process, cache the response for 24 h
    """

    def process_request(self, request):
        if not self._should_check(request):
            return None

        key = request.META.get("HTTP_X_IDEMPOTENCY_KEY", "").strip()

        if not key:
            return JsonResponse(
                {
                    "id": "IDEMPOTENCY_KEY_REQUIRED",
                    "message": "X-Idempotency-Key header is required",
                    "success": False,
                },
                status=400,
            )

        if not UUID4_RE.match(key):
            return JsonResponse(
                {
                    "id": "IDEMPOTENCY_KEY_INVALID",
                    "message": "X-Idempotency-Key must be a valid UUID v4",
                    "success": False,
                },
                status=400,
            )

        user_id = getattr(getattr(request, "user", None), "id", "anon")
        cache_key = f"idempotency:{user_id}:{key}"
        cached = cache.get(cache_key)

        if cached:
            logger.info(
                "Idempotent request — returning cached response",
                extra={"user_id": user_id, "idempotency_key": key},
            )
            payload = json.loads(cached)
            return JsonResponse(payload["body"], status=payload["status_code"])

        # Store key on request so process_response can cache the result
        request._idempotency_cache_key = cache_key
        return None

    def process_response(self, request, response):
        cache_key = getattr(request, "_idempotency_cache_key", None)
        if cache_key and 200 <= response.status_code < 300:
            try:
                body = json.loads(response.content)
                cache.set(
                    cache_key,
                    json.dumps({"status_code": response.status_code, "body": body}),
                    timeout=IDEMPOTENCY_TTL,
                )
            except Exception as e:
                logger.error("Failed to cache idempotency response", extra={"error": str(e)})
        return response

    def _should_check(self, request) -> bool:
        return (
            request.method in IDEMPOTENCY_METHODS
            and any(request.path.startswith(p) for p in IDEMPOTENCY_PATHS)
        )
