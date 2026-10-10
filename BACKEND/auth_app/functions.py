from datetime import datetime, timezone

from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .models import RevokedAccessToken



def create_refresh_token(user):
    return RefreshToken.for_user(user)

def set_auth_cookies(response, refresh):
    response.set_cookie(
        'access_token',
        str(refresh.access_token),
        httponly=True,
    )

    response.set_cookie(
        'refresh_token',
        str(refresh),
        httponly=True,
    )

def blacklist_refresh_token(refresh_token):
    try:
        RefreshToken(refresh_token).blacklist()
    except TokenError:
        pass

def delete_auth_cookies(response):
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')

def get_refresh_token(refresh_token):
    if not refresh_token:
        return None

    try:
        return RefreshToken(refresh_token)
    except TokenError:
        return None

def revoke_access_token(token):
    expires_at = datetime.fromtimestamp(
        token["exp"],
        tz=timezone.utc,
    )

    RevokedAccessToken.objects.get_or_create(
        jti=token["jti"],
        defaults={
            "user_id": token["user_id"],
            "expires_at": expires_at,
        },
    )

def is_access_token_revoked(jti):
    return RevokedAccessToken.objects.filter(
        jti=jti,
    ).exists()
