"""Django admin configuration for quizzes and questions."""

from django.contrib import admin

from .models import Quiz, QuizQuestion


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Configure the quiz list and search tools in admin."""

    list_display = ('id', 'title', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('title', 'description', 'video_url', 'user__username')


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    """Configure the quiz-question list and search tools in admin."""

    list_display = ('id', 'quiz', 'question_title', 'answer', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('question_title', 'answer', 'quiz__title')
