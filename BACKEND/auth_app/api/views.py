from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ..functions import (
    blacklist_refresh_token,
    create_refresh_token,
    delete_auth_cookies,
    get_refresh_token,
    revoke_access_token,
    set_auth_cookies,
)
from ..authentication import enforce_csrf
from .serializers import LoginSerializer, RegistrationSerializer


@ensure_csrf_cookie
def csrf_token_view(request):
    """Return a CSRF token and ensure the browser receives its cookie."""
    return JsonResponse({"csrfToken": get_token(request)})


class RegistrationView(APIView):
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "User created successfully!"},
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    def post(self, request):
        enforce_csrf(request)

        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = serializer.validated_data["user"]
        refresh = create_refresh_token(user)

        response = Response(
            {
                "detail": "Login successfully!",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )

        set_auth_cookies(response, refresh)

        return response


class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            enforce_csrf(request)

        refresh = get_refresh_token(refresh_token)

        if refresh is None:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response(
            {"detail": "Token refreshed successfully!"},
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            "access_token",
            str(refresh.access_token),
            httponly=True,
        )

        return response


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        revoke_access_token(request.auth)

        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            blacklist_refresh_token(refresh_token)

        response = Response(
            {"detail": "Logout successfully!"},
            status=status.HTTP_200_OK,
        )

        delete_auth_cookies(response)

        return response
