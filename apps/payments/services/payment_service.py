"""
Payment business logic lives here, not in views.
Views are thin — they validate input and call services.
"""
import logging
import uuid

from django.db import transaction

from apps.payments.models import Payment, AuditLog
from apps.shared.exceptions import CustomException
from apps.shared.utils.encryption import mask_card

logger = logging.getLogger(__name__)


class PaymentService:

    @staticmethod
    @transaction.atomic
    def create_payment(user, validated_data: dict, idempotency_key: str, ip: str) -> Payment:
        """
        Process a new payment.

        Steps (all inside one DB transaction):
        1. Check if idempotency_key already used
        2. Detect card brand from number
        3. Send to mock gateway
        4. Save payment record
        5. Write audit log
        """
        # 1. Check duplicate
        if Payment.objects.filter(idempotency_key=idempotency_key).exists():
            raise CustomException("PAYMENT_ALREADY_PROCESSED")

        card_number = validated_data.pop("card_number")
        validated_data.pop("card_expiry", None)
        validated_data.pop("card_cvv", None)

        # 2. Card info (we never store full number)
        card_last4 = card_number[-4:]
        card_brand = PaymentService._detect_brand(card_number)

        logger.info(
            f"Processing payment",
            extra={
                "user_id": str(user.id),
                "amount": str(validated_data["amount"]),
                "card": mask_card(card_number),
            },
        )

        # 3. Mock gateway call (replace with Stripe/PayMe/Click in production)
        gateway_ref = PaymentService._call_gateway(
            card_number=card_number,
            amount=validated_data["amount"],
            currency=validated_data.get("currency", "USD"),
        )

        # 4. Save payment
        payment = Payment.objects.create(
            user=user,
            amount=validated_data["amount"],
            currency=validated_data.get("currency", "USD"),
            description=validated_data.get("description", ""),
            card_last4=card_last4,
            card_brand=card_brand,
            gateway_reference=gateway_ref,
            idempotency_key=idempotency_key,
            status=Payment.Status.COMPLETED,
        )

        # 5. Audit log
        AuditLog.objects.create(
            payment=payment,
            action="CREATED",
            new_status=Payment.Status.COMPLETED,
            performed_by=user,
            ip_address=ip,
        )

        return payment

    @staticmethod
    def get_payment(payment_id: str, user) -> Payment:
        try:
            return Payment.objects.get(id=payment_id, user=user)
        except (Payment.DoesNotExist, ValueError):
            raise CustomException("PAYMENT_NOT_FOUND")

    @staticmethod
    def list_payments(user, page: int = 1, page_size: int = 20):
        qs = Payment.objects.filter(user=user)
        total = qs.count()
        offset = (page - 1) * page_size
        payments = qs[offset: offset + page_size]
        return payments, total


    @staticmethod
    def _detect_brand(card_number: str) -> str:
        if card_number.startswith("4"):
            return "visa"
        if card_number[:2] in ("51", "52", "53", "54", "55") or card_number[:4].isdigit() and 2221 <= int(card_number[:4]) <= 2720:
            return "mastercard"
        if card_number[:2] in ("34", "37"):
            return "amex"
        return "unknown"

    @staticmethod
    def _call_gateway(card_number: str, amount, currency: str) -> str:
        """
        Mock payment gateway.
        In production replace with: stripe.PaymentIntent.create(...)
        """
        # Simulate failure for test card ending in 0000
        if card_number.endswith("0000"):
            raise CustomException("PAYMENT_FAILED")

        return f"MOCK-GW-{uuid.uuid4().hex[:12].upper()}"
