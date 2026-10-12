from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase


class LoginTest(APITestCase):
    """Test login behavior and authentication cookies."""

    def setUp(self):
        """Create the user used in login tests."""
        User.objects.create_user(
            username="testuser",
            email="testmail@tester.de",
            password="Testpassword123!",
        )

    def test_login_user(self):
        """Verify successful login and HTTP-only authentication cookies."""
        response = self.client.post(
            "/api/login/",
            {"username": "testuser", "password": "Testpassword123!"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Login successfully!")
        self.assertEqual(response.data["user"]["username"], "testuser")

        for cookie_name in ("access_token", "refresh_token"):
            self.assertIn(cookie_name, response.cookies)
            self.assertTrue(response.cookies[cookie_name]["httponly"])

    def test_login_with_wrong_password(self):
        """Reject invalid credentials without issuing authentication cookies."""
        response = self.client.post(
            "/api/login/",
            {"username": "testuser", "password": "WrongPassword123!"},
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("access_token", response.cookies)
        self.assertNotIn("refresh_token", response.cookies)
