from decimal import Decimal
from rest_framework import serializers

from apps.payments.models import Payment


class CreatePaymentSerializer(serializers.Serializer):
    amount      = serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal("0.01"))
    currency    = serializers.ChoiceField(choices=Payment.Currency.choices, default="USD")
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)
    card_number = serializers.CharField(min_length=13, max_length=19, write_only=True)
    card_expiry = serializers.CharField(max_length=7, write_only=True)  # MM/YYYY
    card_cvv    = serializers.CharField(min_length=3, max_length=4, write_only=True)

    def validate_card_number(self, value: str) -> str:
        cleaned = value.replace(" ", "").replace("-", "")
        if not cleaned.isdigit():
            raise serializers.ValidationError("Card number must contain only digits.")
        if not self._luhn_check(cleaned):
            raise serializers.ValidationError("Invalid card number.")
        return cleaned

    def validate_card_expiry(self, value: str) -> str:
        import re
        from datetime import date
        if not re.match(r"^\d{2}/\d{4}$", value):
            raise serializers.ValidationError("Card expiry must be in MM/YYYY format.")
        month, year = int(value[:2]), int(value[3:])
        if month < 1 or month > 12:
            raise serializers.ValidationError("Invalid expiry month.")
        today = date.today()
        if year < today.year or (year == today.year and month < today.month):
            raise serializers.ValidationError("Card has expired.")
        return value

    def validate_card_cvv(self, value: str) -> str:
        if not value.isdigit():
            raise serializers.ValidationError("CVV must contain only digits.")
        return value

    @staticmethod
    def _luhn_check(number: str) -> bool:
        """Luhn algorithm — validates card number checksum."""
        total = 0
        reverse_digits = number[::-1]
        for i, digit in enumerate(reverse_digits):
            n = int(digit)
            if i % 2 == 1:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
        return total % 10 == 0


class PaymentSerializer(serializers.ModelSerializer):
    """Safe serializer — never exposes full card number."""
    class Meta:
        model  = Payment
        fields = [
            "id", "amount", "currency", "status",
            "description", "card_last4", "card_brand",
            "gateway_reference", "created_at", "updated_at",
        ]
        read_only_fields = fields


class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Payment
        fields = ["id", "amount", "currency", "status", "description", "created_at"]
        read_only_fields = fields
