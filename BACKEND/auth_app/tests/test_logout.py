from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken



class LogoutTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='Testpassword123!',
        )

    def test_logout_user(self):
        refresh = RefreshToken.for_user(self.user)
        access = refresh.access_token

        self.client.cookies['refresh_token'] = str(refresh)
        self.client.cookies['access_token'] = str(access)

        response = self.client.post(
            '/api/logout/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['detail'],
            'Logout successfully!',
        )

        self.assertEqual(
            response.cookies['access_token']['max-age'],
            0,
        )

        self.assertEqual(
            response.cookies['refresh_token']['max-age'],
            0,
        )

    def test_refresh_token_is_invalid_after_logout(self):
        refresh = RefreshToken.for_user(self.user)
        access = refresh.access_token

        self.client.cookies['refresh_token'] = str(refresh)
        self.client.cookies['access_token'] = str(access)

        self.client.post(
            '/api/logout/',
        )

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

    def test_access_token_is_rejected_after_logout(self):
        refresh = RefreshToken.for_user(self.user)
        access = refresh.access_token

        self.client.cookies['refresh_token'] = str(refresh)
        self.client.cookies['access_token'] = str(access)

        self.client.post('/api/logout/')
        self.client.cookies['access_token'] = str(access)

        response = self.client.get('/api/quizzes/')

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_logout_requires_csrf_token(self):
        refresh = RefreshToken.for_user(self.user)
        access = refresh.access_token

        client = APIClient(enforce_csrf_checks=True)
        client.cookies['refresh_token'] = str(refresh)
        client.cookies['access_token'] = str(access)

        response = client.post('/api/logout/')

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_refresh_requires_csrf_token(self):
        refresh = RefreshToken.for_user(self.user)

        client = APIClient(enforce_csrf_checks=True)
        client.cookies['refresh_token'] = str(refresh)

        response = client.post('/api/token/refresh/')

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_logout_accepts_valid_csrf_token(self):
        refresh = RefreshToken.for_user(self.user)
        access = refresh.access_token

        client = APIClient(enforce_csrf_checks=True)
        csrf_response = client.get("/api/csrf/")
        csrf_token = csrf_response.json()["csrfToken"]

        client.cookies["refresh_token"] = str(refresh)
        client.cookies["access_token"] = str(access)

        response = client.post(
            "/api/logout/",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_refresh_accepts_valid_csrf_token(self):
        refresh = RefreshToken.for_user(self.user)

        client = APIClient(enforce_csrf_checks=True)
        csrf_response = client.get("/api/csrf/")
        csrf_token = csrf_response.json()["csrfToken"]

        client.cookies["refresh_token"] = str(refresh)

        response = client.post(
            "/api/token/refresh/",
            HTTP_X_CSRFTOKEN=csrf_token,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
