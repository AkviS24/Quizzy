"""Serializers for registration and login requests."""

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate registration input and create user accounts."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        """Define the user fields accepted during registration."""

        model = User
        fields = ["username", "email", "password", "confirmed_password"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate_email(self, value):
        """Reject an email address that is already registered."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate(self, attrs):
        """Ensure password confirmation matches the submitted password."""
        if attrs["password"] != attrs["confirmed_password"]:
            raise serializers.ValidationError(
                {"confirmed_password": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        """Create a user after removing the confirmation field."""
        validated_data.pop("confirmed_password")
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Validate login credentials and return the authenticated user."""

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """Authenticate the submitted username and password."""
        user = authenticate(
            username=attrs["username"],
            password=attrs["password"],
        )

        if user is None:
            raise serializers.ValidationError(
                {"detail": "Invalid username or password."},
            )

        attrs["user"] = user
        return attrs
