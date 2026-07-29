from django.contrib import admin
from apps.payments.models import Payment, AuditLog


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display  = ["id", "user", "amount", "currency", "status", "card_last4", "created_at"]
    list_filter   = ["status", "currency"]
    search_fields = ["user__email", "gateway_reference", "idempotency_key"]
    readonly_fields = ["id", "idempotency_key", "gateway_reference", "created_at", "updated_at"]
    ordering      = ["-created_at"]


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display  = ["payment", "action", "old_status", "new_status", "performed_by", "created_at"]
    readonly_fields = list_display
    ordering      = ["-created_at"]
