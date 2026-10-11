"""API views for user authentication."""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ..functions import (
    build_login_response,
    build_logout_response,
    build_refresh_response,
    delete_auth_cookies,
    get_refresh_token,
    revoke_auth_tokens,
)
from .serializers import LoginSerializer, RegistrationSerializer


class RegistrationView(APIView):
    """Handle user registration."""

    def post(self, request):
        """Register a user or return validation errors."""
        serializer = RegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(
            {"detail": "User created successfully!"},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """Handle user login."""

    def post(self, request):
        """Authenticate a user and set authentication cookies."""
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_401_UNAUTHORIZED,
            )
        user = serializer.validated_data["user"]
        return build_login_response(user)


class RefreshTokenView(APIView):
    """Handle access-token refresh requests."""

    def post(self, request):
        """Refresh the access token using the refresh-token cookie."""
        token_value = request.COOKIES.get("refresh_token")
        refresh = get_refresh_token(token_value)
        if refresh is None:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return build_refresh_response(refresh)


class LogoutView(APIView):
    """Handle secure user logout."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Revoke authentication tokens and clear their cookies."""
        refresh_token = request.COOKIES.get("refresh_token")
        revoke_auth_tokens(request.auth, refresh_token)
        response = build_logout_response()
        delete_auth_cookies(response)
        return response
