import uuid
from django.conf import settings
from django.db import models


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING    = "pending",    "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED  = "completed",  "Completed"
        FAILED     = "failed",     "Failed"
        REFUNDED   = "refunded",   "Refunded"

    class Currency(models.TextChoices):
        USD = "USD", "US Dollar"
        EUR = "EUR", "Euro"
        UZS = "UZS", "Uzbek Som"

    id                = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user              = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments"
    )
    amount            = models.DecimalField(max_digits=15, decimal_places=2)
    currency          = models.CharField(max_length=3, choices=Currency.choices, default=Currency.USD)
    status            = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    description       = models.TextField(blank=True)

    # Card info — we NEVER store full card number, only last4 + brand
    card_last4        = models.CharField(max_length=4, blank=True)
    card_brand        = models.CharField(max_length=20, blank=True)  # visa / mastercard / etc.

    # Gateway
    gateway_reference = models.CharField(max_length=255, blank=True)

    # Idempotency
    idempotency_key   = models.CharField(max_length=255, unique=True, null=True, blank=True)

    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "payments"
        ordering = ["-created_at"]
        indexes  = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["idempotency_key"]),
        ]

    def __str__(self):
        return f"Payment {self.id} | {self.amount} {self.currency} | {self.status}"


class AuditLog(models.Model):
    """Immutable audit trail for every payment state change."""
    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment     = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name="audit_logs")
    action      = models.CharField(max_length=50)   # e.g. "CREATED", "STATUS_CHANGED"
    old_status  = models.CharField(max_length=20, blank=True)
    new_status  = models.CharField(max_length=20, blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="audit_logs"
    )
    ip_address  = models.GenericIPAddressField(null=True, blank=True)
    note        = models.TextField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"AuditLog {self.action} | Payment {self.payment_id}"
