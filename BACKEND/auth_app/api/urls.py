from django.urls import path

from .views import (
    LoginView,
    LogoutView,
    RefreshTokenView,
    RegistrationView,
)


urlpatterns = [
    path("register/", RegistrationView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
]