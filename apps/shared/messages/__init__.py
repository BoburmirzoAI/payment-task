from typing import TypedDict, Dict


class MessageTemplate(TypedDict):
    id: str
    messages: Dict[str, str]
    status_code: int


MESSAGES: Dict[str, MessageTemplate] = {
    # ── General ──────────────────────────────────────────────────────────────
    "SUCCESS": {
        "id": "SUCCESS",
        "messages": {"en": "Operation completed successfully"},
        "status_code": 200,
    },
    "CREATED": {
        "id": "CREATED",
        "messages": {"en": "Resource created successfully"},
        "status_code": 201,
    },
    "UNKNOWN_ERROR": {
        "id": "UNKNOWN_ERROR",
        "messages": {"en": "An unexpected error occurred"},
        "status_code": 500,
    },
    "VALIDATION_ERROR": {
        "id": "VALIDATION_ERROR",
        "messages": {"en": "Validation failed"},
        "status_code": 400,
    },
    "NOT_FOUND": {
        "id": "NOT_FOUND",
        "messages": {"en": "Resource not found"},
        "status_code": 404,
    },
    "UNAUTHORIZED": {
        "id": "UNAUTHORIZED",
        "messages": {"en": "Authentication credentials were not provided or are invalid"},
        "status_code": 401,
    },
    "PERMISSION_DENIED": {
        "id": "PERMISSION_DENIED",
        "messages": {"en": "You do not have permission to perform this action"},
        "status_code": 403,
    },
    "RATE_LIMIT_EXCEEDED": {
        "id": "RATE_LIMIT_EXCEEDED",
        "messages": {"en": "Too many requests. Please try again later"},
        "status_code": 429,
    },
    # ── Users ─────────────────────────────────────────────────────────────────
    "USER_NOT_FOUND": {
        "id": "USER_NOT_FOUND",
        "messages": {"en": "User not found"},
        "status_code": 404,
    },
    "USER_ALREADY_EXISTS": {
        "id": "USER_ALREADY_EXISTS",
        "messages": {"en": "A user with this email already exists"},
        "status_code": 409,
    },
    "USER_REGISTERED": {
        "id": "USER_REGISTERED",
        "messages": {"en": "User registered successfully"},
        "status_code": 201,
    },
    "INVALID_CREDENTIALS": {
        "id": "INVALID_CREDENTIALS",
        "messages": {"en": "Invalid email or password"},
        "status_code": 401,
    },
    "USER_INACTIVE": {
        "id": "USER_INACTIVE",
        "messages": {"en": "This account has been deactivated"},
        "status_code": 403,
    },
    "TOKEN_REFRESHED": {
        "id": "TOKEN_REFRESHED",
        "messages": {"en": "Token refreshed successfully"},
        "status_code": 200,
    },
    "LOGGED_OUT": {
        "id": "LOGGED_OUT",
        "messages": {"en": "Logged out successfully"},
        "status_code": 200,
    },
    # ── Payments ──────────────────────────────────────────────────────────────
    "PAYMENT_CREATED": {
        "id": "PAYMENT_CREATED",
        "messages": {"en": "Payment initiated successfully"},
        "status_code": 201,
    },
    "PAYMENT_NOT_FOUND": {
        "id": "PAYMENT_NOT_FOUND",
        "messages": {"en": "Payment not found"},
        "status_code": 404,
    },
    "PAYMENT_ALREADY_PROCESSED": {
        "id": "PAYMENT_ALREADY_PROCESSED",
        "messages": {"en": "This payment has already been processed"},
        "status_code": 409,
    },
    "PAYMENT_FAILED": {
        "id": "PAYMENT_FAILED",
        "messages": {"en": "Payment processing failed"},
        "status_code": 402,
    },
    "PAYMENT_LIST_FETCHED": {
        "id": "PAYMENT_LIST_FETCHED",
        "messages": {"en": "Payments fetched successfully"},
        "status_code": 200,
    },
    "PAYMENT_FETCHED": {
        "id": "PAYMENT_FETCHED",
        "messages": {"en": "Payment fetched successfully"},
        "status_code": 200,
    },
    "IDEMPOTENCY_KEY_REQUIRED": {
        "id": "IDEMPOTENCY_KEY_REQUIRED",
        "messages": {"en": "X-Idempotency-Key header is required"},
        "status_code": 400,
    },
    "IDEMPOTENCY_KEY_INVALID": {
        "id": "IDEMPOTENCY_KEY_INVALID",
        "messages": {"en": "X-Idempotency-Key must be a valid UUID v4"},
        "status_code": 400,
    },
    "INSUFFICIENT_FUNDS": {
        "id": "INSUFFICIENT_FUNDS",
        "messages": {"en": "Insufficient funds to complete this payment"},
        "status_code": 402,
    },
}
