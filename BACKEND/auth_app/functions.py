"""Helper functions for authentication and token management."""

from datetime import datetime, timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import RevokedAccessToken


LOGOUT_SUCCESS_DETAIL = (
    "Log-Out successfully! All Tokens will be deleted. "
    "Refresh token is now invalid."
)


def create_refresh_token(user):
    """Create a refresh token for the given user."""
    return RefreshToken.for_user(user)


def build_login_response(user):
    """Build the successful login response with authentication cookies."""
    refresh = create_refresh_token(user)
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
    }
    response = Response(
        {"detail": "Login successfully!", "user": user_data},
        status=status.HTTP_200_OK,
    )
    set_auth_cookies(response, refresh)
    return response


def build_refresh_response(refresh):
    """Build a response with a renewed access token."""
    response = Response(
        {"detail": "Token refreshed"},
        status=status.HTTP_200_OK,
    )
    response.set_cookie(
        "access_token",
        str(refresh.access_token),
        httponly=True,
    )
    return response


def build_logout_response():
    """Build the documented successful logout response."""
    return Response(
        {"detail": LOGOUT_SUCCESS_DETAIL},
        status=status.HTTP_200_OK,
    )


def set_auth_cookies(response, refresh):
    """Set the HTTP-only access and refresh token cookies."""
    response.set_cookie("access_token", str(refresh.access_token), httponly=True)
    response.set_cookie("refresh_token", str(refresh), httponly=True)


def blacklist_refresh_token(refresh_token):
    """Blacklist a refresh token if it is valid."""
    try:
        RefreshToken(refresh_token).blacklist()
    except TokenError:
        pass


def delete_auth_cookies(response):
    """Delete the authentication cookies from a response."""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


def get_refresh_token(refresh_token):
    """Return a valid refresh token, or None if it is invalid."""
    if not refresh_token:
        return None
    try:
        return RefreshToken(refresh_token)
    except TokenError:
        return None


def revoke_access_token(token):
    """Store an access token identifier to prevent its reuse."""
    expires_at = datetime.fromtimestamp(token["exp"], tz=timezone.utc)
    RevokedAccessToken.objects.get_or_create(
        jti=token["jti"],
        defaults={
            "user_id": token["user_id"],
            "expires_at": expires_at,
        },
    )


def is_access_token_revoked(jti):
    """Return whether an access token has been revoked."""
    return RevokedAccessToken.objects.filter(jti=jti).exists()


def revoke_auth_tokens(access_token, refresh_token):
    """Revoke the access token and blacklist the refresh token."""
    revoke_access_token(access_token)
    if refresh_token:
        blacklist_refresh_token(refresh_token)
