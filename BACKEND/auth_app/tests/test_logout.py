from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class LogoutTest(APITestCase):
    """Test logout behavior and token invalidation."""

    def setUp(self):
        """Create the user used in logout tests."""
        self.user = User.objects.create_user(
            username="testuser",
            password="Testpassword123!",
        )

    def _set_auth_cookies(self):
        """Create authentication tokens and attach them to the client."""
        refresh = RefreshToken.for_user(self.user)
        access = refresh.access_token
        self.client.cookies["refresh_token"] = str(refresh)
        self.client.cookies["access_token"] = str(access)
        return refresh, access

    def test_logout_user(self):
        """Verify logout succeeds and expires both authentication cookies."""
        self._set_auth_cookies()
        response = self.client.post("/api/logout/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data["detail"],
            "Log-Out successfully! All Tokens will be deleted. "
            "Refresh token is now invalid.",
        )
        self.assertEqual(response.cookies["access_token"]["max-age"], 0)
        self.assertEqual(response.cookies["refresh_token"]["max-age"], 0)

    def test_refresh_token_is_invalid_after_logout(self):
        """Reject refresh attempts after logout invalidates the refresh token."""
        self._set_auth_cookies()
        self.client.post("/api/logout/")
        response = self.client.post("/api/token/refresh/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertNotIn("access_token", response.cookies)

    def test_access_token_is_rejected_after_logout(self):
        """Verify an access token cannot be reused after logout."""
        _, access = self._set_auth_cookies()
        self.client.post("/api/logout/")
        self.client.cookies["access_token"] = str(access)
        response = self.client.get("/api/quizzes/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_with_invalid_refresh_token(self):
        """Allow logout when the refresh token is invalid."""
        _, access = self._set_auth_cookies()
        self.client.cookies["refresh_token"] = "invalid-token"

        response = self.client.post("/api/logout/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.cookies["access_token"]["max-age"], 0)
        self.assertEqual(response.cookies["refresh_token"]["max-age"], 0)
