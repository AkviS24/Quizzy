from rest_framework.authentication import CSRFCheck
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication

from .functions import is_access_token_revoked


def enforce_csrf(request):
    """Reject requests that fail Django's CSRF validation."""
    def dummy_get_response(request):
        return None

    check = CSRFCheck(dummy_get_response)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})

    if reason:
        raise PermissionDenied(f"CSRF Failed: {reason}")


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate requests using JWTs stored in cookies."""

    def authenticate(self, request):
        """Validate the access token and enforce CSRF protection."""
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return None

        validated_token = self.get_validated_token(access_token)

        if is_access_token_revoked(validated_token["jti"]):
            raise AuthenticationFailed("Access token has been revoked.")

        enforce_csrf(request)

        return self.get_user(validated_token), validated_token
