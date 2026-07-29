import json
import logging
import time

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse

logger = logging.getLogger(__name__)

# Endpoints that need stricter limits
AUTH_PATHS = ["/api/v1/auth/login", "/api/v1/auth/register"]
PAYMENT_PATHS = ["/api/v1/payments"]


class RateLimitMiddleware:
    """
    Redis-based sliding window rate limiter.

    Strategy:
    - Auth endpoints   → 10 req / 15 min  (brute-force protection)
    - Payment endpoints → 10 req / 1 min  (fraud prevention)
    - Everything else  → 100 req / 1 min  (general protection)

    Key: rl:<type>:<ip>:<user_id_or_anon>
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        config, prefix = self._get_config(request.path)
        ip = self._get_ip(request)
        user_id = getattr(getattr(request, "user", None), "id", "anon")
        cache_key = f"rl:{prefix}:{ip}:{user_id}"

        if self._is_limited(cache_key, config):
            logger.warning("Rate limit exceeded", extra={"ip": ip, "path": request.path})
            return JsonResponse(
                {
                    "id": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please try again later.",
                    "success": False,
                },
                status=429,
            )

        response = self.get_response(request)
        return response

    # ── helpers ───────────────────────────────────────────────────────────────

    def _get_config(self, path: str):
        if any(path.startswith(p) for p in AUTH_PATHS):
            return settings.RATE_LIMIT_AUTH, "auth"
        if any(path.startswith(p) for p in PAYMENT_PATHS):
            return settings.RATE_LIMIT_PAYMENT, "payment"
        return settings.RATE_LIMIT_GENERAL, "general"

    def _get_ip(self, request) -> str:
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")

    def _is_limited(self, cache_key: str, config: dict) -> bool:
        """
        Sliding window counter using Redis sorted sets via django-redis.
        Each entry is timestamped; old ones are pruned on every request.
        """
        now = time.time()
        window = config["window"]
        max_requests = config["requests"]
        window_start = now - window

        # We store a list of timestamps as a JSON blob
        raw = cache.get(cache_key)
        timestamps: list = json.loads(raw) if raw else []

        # Prune entries outside window
        timestamps = [t for t in timestamps if t > window_start]

        if len(timestamps) >= max_requests:
            return True  # Limited

        timestamps.append(now)
        cache.set(cache_key, json.dumps(timestamps), timeout=window + 1)
        return False
