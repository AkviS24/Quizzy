from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

from .functions import is_access_token_revoked


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate requests using JWTs stored in cookies."""

    def authenticate(self, request):
        """Validate the access token and reject revoked tokens."""
        access_token = request.COOKIES.get("access_token")

        if not access_token:
            return None

        validated_token = self.get_validated_token(access_token)

        if is_access_token_revoked(validated_token["jti"]):
            raise AuthenticationFailed("Access token has been revoked.")

        return self.get_user(validated_token), validated_token
