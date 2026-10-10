"""Functions for creating quizzes from YouTube videos."""

from django.db import transaction

from . import media_utils, utils
from .models import Quiz, QuizQuestion


class QuizGenerationError(Exception):
    """Raised when video processing or quiz generation fails."""


def create_quiz_from_youtube_url(url, user):
    """Transcribe a video and save its generated quiz."""
    try:
        _, transcript = media_utils.transcribe_youtube_video(url)
        generated_quiz = utils.generate_quiz_from_transcript(transcript)
    except Exception as error:
        raise QuizGenerationError(
            "Video processing or quiz generation failed."
        ) from error

    return _save_generated_quiz(url, user, generated_quiz)


@transaction.atomic
def _save_generated_quiz(url, user, generated_quiz):
    """Save a generated quiz and all its questions."""
    quiz = Quiz.objects.create(
        user=user,
        title=generated_quiz["title"],
        description=generated_quiz["description"],
        video_url=url,
    )
    _save_questions(quiz, generated_quiz["questions"])
    return quiz


def _save_questions(quiz, questions):
    """Create all questions belonging to a quiz."""
    quiz_questions = [
        QuizQuestion(quiz=quiz, **question)
        for question in questions
    ]
    QuizQuestion.objects.bulk_create(quiz_questions)
