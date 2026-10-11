"""API views for managing quizzes."""

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..functions import (
    QuizGenerationError,
    build_quiz_creation_error_response,
    create_quiz_from_youtube_url,
)
from ..media_utils import validate_youtube_url
from ..models import Quiz
from .serializers import QuizSerializer


class QuizListCreateView(generics.ListCreateAPIView):
    """List the user's quizzes and create new quizzes."""

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return the user's quizzes, newest first."""
        return Quiz.objects.filter(
            user=self.request.user,
        ).order_by("-created_at", "-pk")

    def create(self, request, *args, **kwargs):
        """Create a quiz from the submitted YouTube URL."""
        try:
            url = validate_youtube_url(request.data.get("url"))
            quiz = create_quiz_from_youtube_url(url, request.user)
        except (ValueError, QuizGenerationError) as error:
            return build_quiz_creation_error_response(error)
        serializer = self.get_serializer(quiz)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete the user's quiz."""

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    queryset = Quiz.objects.all()

    def get_object(self):
        """Prevent access to quizzes owned by another user."""
        quiz = super().get_object()

        if quiz.user != self.request.user:
            raise PermissionDenied(
                "You don't have permission to access this quiz.",
            )

        return quiz
