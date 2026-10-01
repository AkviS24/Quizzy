from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase



class LoginTest(APITestCase):
    def setUp(self):
        User.objects.create_user(
            username='testuser',
            email='testmail@tester.de',
            password='Testpassword123!',
        )

    def test_login_user(self):
        response = self.client.post(
            '/api/login/',
            {
                'username': 'testuser',
                'password': 'Testpassword123!',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data['detail'],
            'Login successfully!',
        )

        self.assertEqual(
            response.data['user']['username'],
            'testuser',
        )

        self.assertIn(
            'access_token',
            response.cookies,
        )

        self.assertIn(
            'refresh_token',
            response.cookies,
        )

        self.assertTrue(
            response.cookies['access_token']['httponly'],
        )

        self.assertTrue(
            response.cookies['refresh_token']['httponly'],
        )

    def test_login_with_wrong_password(self):
        response = self.client.post(
            '/api/login/',
            {
                'username': 'testuser',
                'password': 'WrongPassword123!',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertNotIn(
            'access_token',
            response.cookies,
        )

        self.assertNotIn(
            'refresh_token',
            response.cookies,
        )