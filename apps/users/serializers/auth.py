from django.contrib.auth import get_user_model
from rest_framework import serializers
import re

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, label="Confirm password")

    class Meta:
        model  = User
        fields = ["phone_number", "full_name", "password", "password2"]
        extra_kwargs = {
            "phone_number": {"validators": []}
        }

    def validate_phone_number(self, value: str) -> str:
        if not re.match(r'^\+?[1-9]\d{9,14}$', value):
            raise serializers.ValidationError("Enter a valid phone number (e.g. +998901234567).")
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password2"):
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password     = serializers.CharField(write_only=True)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ["id", "phone_number", "full_name", "role", "created_at"]
        read_only_fields = fields