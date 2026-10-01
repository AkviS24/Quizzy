from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken



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