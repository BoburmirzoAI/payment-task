import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from apps.shared.exceptions.base import CustomException
from apps.shared.exceptions.translator import get_message_detail

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Global DRF exception handler.
    Converts all exceptions into our standard response format.
    """
    # Handle our own CustomException
    if isinstance(exc, CustomException):
        request = context.get("request")
        lang = _get_lang(request)
        detail = get_message_detail(exc.message_key, lang=lang, context=exc.context)
        return Response(
            {"id": detail["id"], "message": detail["message"], "success": False},
            status=detail["status_code"],
        )

    # Let DRF handle its own exceptions first
    response = exception_handler(exc, context)

    if response is not None:
        request = context.get("request")
        lang = _get_lang(request)

        # Map DRF status codes to our message keys
        status_map = {
            401: "UNAUTHORIZED",
            403: "PERMISSION_DENIED",
            404: "NOT_FOUND",
            405: "UNKNOWN_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
        }

        message_key = status_map.get(response.status_code, "UNKNOWN_ERROR")
        detail = get_message_detail(message_key, lang=lang)

        # Preserve validation errors from DRF
        errors = None
        if response.status_code == 400:
            errors = response.data
            detail = get_message_detail("VALIDATION_ERROR", lang=lang)

        body = {
            "id": detail["id"],
            "message": detail["message"],
            "success": False,
        }
        if errors:
            body["errors"] = errors

        response.data = body

    else:
        # Unhandled exception — return 500
        logger.exception(f"Unhandled exception: {exc}")
        detail = get_message_detail("UNKNOWN_ERROR")
        response = Response(
            {"id": detail["id"], "message": detail["message"], "success": False},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return response


def _get_lang(request) -> str:
    if request and hasattr(request, "headers"):
        accept_lang = request.headers.get("Accept-Language", "en")
        return accept_lang.split(";")[0].split(",")[0].strip()
    return "en"
