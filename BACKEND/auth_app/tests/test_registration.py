from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase



class RegistrationTests(APITestCase):
    def test_register_user(self):
        response = self.client.post(
            '/api/register/',
            {
                'username': 'testuser',
                'email': 'testmail@tester.com',
                'password': 'Testpassword123!',
                'confirmed_password': 'Testpassword123!',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertEqual(
            User.objects.count(),
            1,
        )

        self.assertTrue(
            User.objects.filter(username='testuser').exists(),
        )

    def test_password_do_not_match(self):
        response = self.client.post(
            '/api/register/',
            {
                'username': 'testuser',
                'email': 'test@tester.de',
                'password': 'Testpassword123!',
                'confirmed_password': 'DifferentTestPassword123!',
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            User.objects.count(),
            0,
        )