from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from quiz_app.models import Quiz


class QuizListCreateViewTest(TestCase):
    """Tests listing and creating quizzes."""

    def setUp(self):
        """Prepare the API client and test user."""

        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='Testpassword123!',
        )
        self.url = '/api/quizzes/'

    def test_unauthenticated_user_cannot_list_quizzes(self):
        """Reject quiz-list requests from unauthenticated users."""

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unauthenticated_user_cannot_create_quiz(self):
        """Reject quiz creation requests from unauthenticated users."""

        response = self.client.post(
            self.url,
            {},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    @patch('quiz_app.utils.generate_quiz_from_transcript')
    @patch('quiz_app.media_utils.transcribe_youtube_video')
    def test_authenticated_user_can_create_quiz(
        self,
        mock_transcribe,
        mock_generate,
    ):
        """Create a quiz for the authenticated user using mocked processing."""

        self.client.force_authenticate(user=self.user)
        video_url = 'https://www.youtube.com/watch?v=test123'
        mock_transcribe.return_value = ('Testvideo', 'Testtranskript')
        mock_generate.return_value = {
            'title': 'Test Quiz',
            'description': 'Test description',
            'questions': [
                {
                    'question_title': 'Question 1',
                    'question_options': ['A', 'B', 'C', 'D'],
                    'answer': 'A',
                },
            ],
        }

        response = self.client.post(
            self.url,
            {'url': video_url},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 1)

        quiz = Quiz.objects.get()
        self.assertEqual(quiz.user, self.user)
        self.assertEqual(quiz.title, 'Test Quiz')
        self.assertEqual(quiz.description, 'Test description')
        self.assertEqual(quiz.video_url, video_url)

    @patch('quiz_app.utils.generate_quiz_from_transcript')
    @patch('quiz_app.media_utils.transcribe_youtube_video')
    def test_user_cannot_assign_quiz_to_another_user(
        self,
        mock_transcribe,
        mock_generate,
    ):
        """Ensure client input cannot assign a quiz to another user."""

        other_user = User.objects.create_user(
            username='otheruser',
            password='Otherpassword123!',
        )
        self.client.force_authenticate(user=self.user)
        video_url = 'https://www.youtube.com/watch?v=test123'
        mock_transcribe.return_value = ('Testvideo', 'Testtranskript')
        mock_generate.return_value = {
            'title': 'Test Quiz',
            'description': 'Test description',
            'questions': [
                {
                    'question_title': 'Question 1',
                    'question_options': ['A', 'B', 'C', 'D'],
                    'answer': 'A',
                },
            ],
        }

        response = self.client.post(
            self.url,
            {'url': video_url, 'user': other_user.pk},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        quiz = Quiz.objects.get(title='Test Quiz')
        self.assertEqual(quiz.user, self.user)
        self.assertNotEqual(quiz.user, other_user)

    def test_quizzes_are_ordered_newest_first(self):
        """Return newest quizzes before older ones."""

        self.client.force_authenticate(user=self.user)
        for title in ("Older Quiz", "Newer Quiz"):
            Quiz.objects.create(
                user=self.user, title=title, description=title,
                video_url=f"https://www.youtube.com/watch?v={title.replace(' ', '').lower()}",
            )
        response = self.client.get(self.url)
        self.assertEqual(
            [quiz["title"] for quiz in response.data],
            ["Newer Quiz", "Older Quiz"],
        )

    def test_authenticated_user_can_list_own_quizzes(self):
        """Return quizzes owned by the authenticated user."""

        self.client.force_authenticate(user=self.user)

        Quiz.objects.create(
            user=self.user,
            title='Own Quiz',
            description='Own description',
            video_url='https://www.youtube.com/watch?v=own123',
        )

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Own Quiz')

    def test_user_can_only_list_own_quizzes(self):
        """Exclude quizzes owned by other users from the list response."""

        other_user = User.objects.create_user(
            username='otheruser',
            password='Otherpassword123!',
        )

        Quiz.objects.create(
            user=self.user,
            title='Own Quiz',
            description='Own description',
            video_url='https://www.youtube.com/watch?v=own123',
        )

        Quiz.objects.create(
            user=other_user,
            title='Other Quiz',
            description='Other description',
            video_url='https://www.youtube.com/watch?v=other123',
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(
            response.data[0]['title'],
            'Own Quiz',
        )


class QuizDetailViewTest(TestCase):
    """Test retrieving a single quiz."""

    def setUp(self):
        """Create a user-owned quiz and its detail endpoint."""

        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='Testpassword123!',
        )
        self.quiz = Quiz.objects.create(
            user=self.user,
            title='Own Quiz',
            description='Own description',
            video_url='https://www.youtube.com/watch?v=own123',
        )
        self.url = f'/api/quizzes/{self.quiz.pk}/'

    def test_unauthenticated_user_cannot_retrieve_quiz(self):
        """Ensure retrieving a quiz requires authentication."""

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_unauthenticated_user_cannot_update_or_delete_quiz(self):
        """Ensure updating and deleting a quiz requires authentication."""

        update_response = self.client.patch(
            self.url,
            {'title': 'Unauthorized update'},
            format='json',
        )
        delete_response = self.client.delete(self.url)

        self.assertEqual(
            update_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            delete_response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

        self.quiz.refresh_from_db()
        self.assertEqual(
            self.quiz.title,
            'Own Quiz',
        )

    def test_authenticated_user_can_retrieve_own_quiz(self):
        """Return the details of a quiz owned by the authenticated user."""

        self.client.force_authenticate(user=self.user)

        response = self.client.get(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data['id'],
            self.quiz.pk,
        )
        self.assertEqual(
            response.data['title'],
            'Own Quiz',
        )
        self.assertEqual(
            response.data['description'],
            'Own description',
        )
        self.assertEqual(
            response.data['video_url'],
            'https://www.youtube.com/watch?v=own123',
        )

    def test_nonexistent_quiz_returns_not_found(self):
        """Ensure a nonexistent quiz returns a 404 response."""

        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/quizzes/9999999/')

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_user_cannot_retrieve_another_users_quiz(self):
        """Deny access to a quiz owned by another user."""

        other_user = User.objects.create_user(
            username='otheruser',
            password='Otheruserpassword123!',
        )
        other_quiz = Quiz.objects.create(
            user=other_user,
            title='Other Quiz',
            description='Other description',
            video_url='https://www.youtube.com/watch?v=other123',
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/api/quizzes/{other_quiz.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_authenticated_user_can_update_own_quiz(self):
        """Allow the owner to update the quiz title and description."""

        self.client.force_authenticate(user=self.user)

        data = {
            'title': 'Updated Quiz',
            'description': 'Updated description',
            'video_url': self.quiz.video_url,
        }

        response = self.client.patch(
            self.url,
            data,
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.quiz.refresh_from_db()

        self.assertEqual(
            self.quiz.title,
            'Updated Quiz',
        )
        self.assertEqual(
            self.quiz.description,
            'Updated description',
        )
        self.assertEqual(
            self.quiz.video_url,
            'https://www.youtube.com/watch?v=own123',
        )

    def test_user_cannot_change_video_url(self):
        """Ensure a quiz update cannot replace its original video URL."""

        self.client.force_authenticate(user=self.user)
        original_video_url = self.quiz.video_url

        response = self.client.patch(
            self.url,
            {'video_url': 'https://youtube.com/watch?v=changed123'},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.quiz.refresh_from_db()

        self.assertEqual(
            self.quiz.video_url,
            original_video_url,
        )

    def test_user_cannot_update_another_users_quiz(self):
        """Reject updates to quizzes owned by other users."""

        other_user = User.objects.create_user(
            username='otheruser',
            password='Otherpassword123!',
        )
        other_quiz = Quiz.objects.create(
            user=other_user,
            title='Other Quiz',
            description='Other description',
            video_url='https://www.youtube.com/watch?v=other123',
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.patch(
            f'/api/quizzes/{other_quiz.pk}/',
            {'title': 'Changed by another user'},
            format='json',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        other_quiz.refresh_from_db()

        self.assertEqual(
            other_quiz.title,
            'Other Quiz',
        )

    def test_authenticated_user_can_delete_own_quiz(self):
        """Allow the owner to delete their quiz."""

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.url)

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertFalse(
            Quiz.objects.filter(pk=self.quiz.pk).exists(),
        )

    def test_user_cannot_delete_another_users_quiz(self):
        """Reject deletion attempts against another user's quiz."""

        other_user = User.objects.create_user(
            username='otheruser',
            password='Otherpassword123!',
        )
        other_quiz = Quiz.objects.create(
            user=other_user,
            title='Other Quiz',
            description='Other description',
            video_url='https://www.youtube.com/watch?v=other123',
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.delete(
            f'/api/quizzes/{other_quiz.pk}/',
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertTrue(
            Quiz.objects.filter(pk=other_quiz.pk).exists(),
        )
