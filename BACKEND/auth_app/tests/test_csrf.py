from rest_framework import status
from rest_framework.test import APITestCase


class CsrfTokenTests(APITestCase):
    """Test the endpoint that provides CSRF tokens to the frontend."""

    def test_csrf_endpoint_returns_token_and_sets_cookie(self):
        """Return a CSRF token and set the corresponding cookie."""
        response = self.client.get("/api/csrf/")
        payload = response.json()

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertIn("csrfToken", payload)
        self.assertTrue(payload["csrfToken"])
        self.assertIn("csrftoken", response.cookies)
