from django.contrib.auth.models import User
from django.db import models



class Quiz(models.Model):
    """Stores a quiz and its associated YouTube video."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="quizzes",
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    video_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class QuizQuestion(models.Model):
    """Stores a question and its 4 possible answers."""

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    question_title = models.TextField()
    question_options = models.JSONField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)