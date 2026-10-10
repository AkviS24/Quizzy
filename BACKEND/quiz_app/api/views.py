"""API views for managing quizzes."""

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..functions import (
    QuizGenerationError,
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
        """Return only quizzes owned by the current user."""
        return Quiz.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Create a quiz from the submitted YouTube URL."""
        try:
            url = validate_youtube_url(request.data.get("url"))
        except ValueError as error:
            return Response(
                {"detail": str(error)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quiz = create_quiz_from_youtube_url(url, request.user)
        except QuizGenerationError:
            return Response(
                {"detail": "Das Video konnte nicht verarbeitet werden."},
                status=status.HTTP_502_BAD_GATEWAY,
            )

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
