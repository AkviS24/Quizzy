from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken



class RefreshTokenTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='Testpassword123!',
        )

    def test_refresh_token(self):
        refresh = RefreshToken.for_user(self.user)

        self.client.cookies['refresh_token'] = str(refresh)

        response = self.client.post(
            '/api/token/refresh/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['detail'],
            'Token refreshed successfully!',
        )

        self.assertIn(
            'access_token',
            response.cookies,
        )

        self.assertTrue(
            response.cookies['access_token']['httponly'],
        )

    def test_refresh_without_token(self):
        response = self.client.post(
            '/api/token/refresh/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertNotIn(
            'access_token',
            response.cookies,
        )

    def test_refresh_with_invalid_token(self):
        self.client.cookies['refresh_token'] = 'invalid-token'

        response = self.client.post(
            '/api/token/refresh/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.assertNotIn(
            'access_token',
            response.cookies,
        )