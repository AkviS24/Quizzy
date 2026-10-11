"""Serializers for quiz data returned by the REST API."""

from rest_framework import serializers

from ..models import Quiz, QuizQuestion


class QuizQuestionSerializer(serializers.ModelSerializer):
    """Serializes quiz questions and validates their answer options."""

    class Meta:
        """Declare the fields exposed for quiz questions."""

        model = QuizQuestion
        fields = [
            'id',
            'question_title',
            'question_options',
            'answer',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_question_options(self, value):
        """Require exactly four string answer options."""
        if len(value) != 4:
            raise serializers.ValidationError(
                'A question must have exactly 4 options.',
            )

        if not all(isinstance(option, str) for option in value):
            raise serializers.ValidationError(
                'All question options must be strings.',
            )

        return value

    def validate(self, attrs):
        """Ensure the correct answer is among the provided options."""
        options = attrs.get('question_options')
        answer = attrs.get('answer')

        if options is not None and answer is not None:
            if answer not in options:
                raise serializers.ValidationError({
                    'answer': ('The correct answer must be one of the four options.'),
                })

        return attrs


class QuizSerializer(serializers.ModelSerializer):
    """Serialize quizzes including their associated questions."""

    questions = QuizQuestionSerializer(many=True, read_only=True)

    def get_fields(self):
        """Make the video-URL read_only when updating a quiz."""
        fields = super().get_fields()

        if self.instance is not None:
            fields['video_url'].read_only = True

        return fields

    class Meta:
        """Declare the fields exposed for a quiz."""

        model = Quiz
        fields = [
            'id',
            'title',
            'description',
            'created_at',
            'updated_at',
            'video_url',
            'questions',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'questions',
        ]
