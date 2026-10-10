from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated

from .serializers import QuizSerializer
from ..models import Quiz



class QuizListCreateView(generics.ListCreateAPIView):
    """List the user's quizzes and create new quizzes."""

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Quiz.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class QuizDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update and delete the user's quiz."""

    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated]
    queryset = Quiz.objects.all()

    def get_object(self):
        quiz = super().get_object()

        if quiz.user != self.request.user:
            raise PermissionDenied(
                "You don't have permission to access this quiz.",
            )

        return quiz