from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class RefreshTokenTest(APITestCase):
    """Test refresh-token handling and access-token cookies."""

    def setUp(self):
        """Create the user used in refresh-token tests."""
        self.user = User.objects.create_user(
            username="testuser",
            password="Testpassword123!",
        )

    def test_refresh_token(self):
        """Verify a valid refresh token issues a new access-token cookie."""
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["refresh_token"] = str(refresh)
        response = self.client.post("/api/token/refresh/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Token refreshed")
        self.assertIn("access_token", response.cookies)
        self.assertTrue(response.cookies["access_token"]["httponly"])

    def test_refresh_without_token(self):
        """Reject a refresh request when no refresh token is provided."""
        response = self.client.post("/api/token/refresh/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertNotIn("access_token", response.cookies)

    def test_refresh_with_invalid_token(self):
        """Reject a refresh request containing an invalid token."""
        self.client.cookies["refresh_token"] = "invalid-token"
        response = self.client.post("/api/token/refresh/")

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertNotIn("access_token", response.cookies)
