"""Tests for creating quizzes from YouTube videos."""

from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from quiz_app.models import Quiz, QuizQuestion


def build_generated_quiz():
    """Return a valid mock quiz containing ten questions."""
    questions = [
        {
            "question_title": f"Question {number}",
            "question_options": ["A", "B", "C", "D"],
            "answer": "A",
        }
        for number in range(1, 11)
    ]
    return {
        "title": "Testvideo-Quiz",
        "description": "Generiertes Testquiz",
        "questions": questions,
    }


class QuizGenerationAPITests(TestCase):
    """Test the documented YouTube-to-quiz API contract."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="quiz_creator",
            password="Testpassword123!",
        )
        self.url = "/api/quizzes/"
        self.video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.client.force_authenticate(user=self.user)

    def test_invalid_youtube_url_returns_bad_request(self):
        response = self.client.post(
            self.url,
            {"url": "https://example.com/video"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("quiz_app.utils.generate_quiz_from_transcript")
    @patch("quiz_app.media_utils.transcribe_youtube_video")
    def test_valid_url_creates_quiz_and_ten_questions(
        self,
        mock_transcribe,
        mock_generate,
    ):
        mock_transcribe.return_value = ("Testvideo", "Ein Testtranskript.")
        mock_generate.return_value = build_generated_quiz()

        response = self.client.post(
            self.url,
            {"url": self.video_url},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 1)
        self.assertEqual(QuizQuestion.objects.count(), 10)

        quiz = Quiz.objects.get()
        self.assertEqual(quiz.user, self.user)
        self.assertEqual(quiz.video_url, self.video_url)
        self.assertEqual(quiz.title, "Testvideo-Quiz")
        mock_transcribe.assert_called_once_with(self.video_url)
        mock_generate.assert_called_once_with("Ein Testtranskript.")

    def test_unauthenticated_user_cannot_generate_quiz(self):
        self.client.force_authenticate(user=None)
        response = self.client.post(
            self.url,
            {"url": self.video_url},
            format="json",
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    @patch("quiz_app.media_utils.transcribe_youtube_video")
    def test_transcription_failure_returns_bad_gateway(
        self,
        mock_transcribe,
    ):
        from quiz_app.functions import QuizGenerationError

        mock_transcribe.side_effect = QuizGenerationError(
            "Interne technische Details"
        )

        response = self.client.post(
            self.url,
            {"url": self.video_url},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertNotIn("Interne technische Details", str(response.data))
        self.assertEqual(Quiz.objects.count(), 0)

    @patch("quiz_app.utils.generate_quiz_from_transcript")
    @patch("quiz_app.media_utils.transcribe_youtube_video")
    def test_quiz_generation_failure_returns_bad_gateway(
        self,
        mock_transcribe,
        mock_generate,
    ):
        from quiz_app.functions import QuizGenerationError

        mock_transcribe.return_value = ("Testvideo", "Testtranskript")
        mock_generate.side_effect = QuizGenerationError(
            "Interne technische Details"
        )

        response = self.client.post(
            self.url,
            {"url": self.video_url},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertNotIn("Interne technische Details", str(response.data))
        self.assertEqual(Quiz.objects.count(), 0)