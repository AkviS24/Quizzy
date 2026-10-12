from django.contrib.auth.models import User
from django.test import TestCase

from quiz_app.api.serializers import QuizSerializer, QuizQuestionSerializer
from quiz_app.models import Quiz, QuizQuestion


class QuizQuestionSerializerTests(TestCase):
    """Tests validation and serialization of quiz questions."""

    def setUp(self):
        """Create a user and quiz for question serializer tests."""

        self.user = User.objects.create_user(
            username='testuser',
            password='Testpassword123!',
        )
        self.quiz = Quiz.objects.create(
            user=self.user,
            title='Test Quiz',
            description='Test description',
            video_url='https://www.youtube.com/watch?v=test123',
        )

    def test_valid_question_options(self):
        """Verify a question with four options is serialized correctly."""

        question = QuizQuestion(
            quiz=self.quiz,
            question_title='What is Python?',
            question_options=[
                'A programming language',
                'A database',
                'A browser',
                'An operating system',
            ],
            answer='A programming language',
        )

        serializer = QuizQuestionSerializer(question)

        self.assertEqual(
            len(serializer.data['question_options']),
            4,
        )

    def test_valid_answer_is_accepted(self):
        """Accept an answer that matches one of the available options."""

        data = {
            'question_title': 'What is Python?',
            'question_options': [
                'A programming language',
                'A database',
                'A browser',
                'An operating system',
            ],
            'answer': 'A programming language',
        }

        serializer = QuizQuestionSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_answer_not_in_options_is_rejected(self):
        """Reject an answer that is not among the available options."""

        data = {
            'question_title': 'What is Python?',
            'question_options': [
                'A programming language',
                'A database',
                'A browser',
                'An operating system',
            ],
            'answer': 'A web server',
        }

        serializer = QuizQuestionSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('answer', serializer.errors)

    def test_question_options_require_four_items(self):
        """Reject questions that do not provide exactly four options."""

        data = {
            'question_title': 'What is Python?',
            'question_options': [
                'A programming language',
                'A database',
                'A browser',
            ],
            'answer': 'A programming language',
        }

        serializer = QuizQuestionSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('question_options', serializer.errors)

    def test_question_options_must_be_strings(self):
        """Reject question options that are not strings."""

        data = {
            'question_title': 'What is Python?',
            'question_options': [
                'A programming language',
                'A database',
                123,
                'An operating system',
            ],
            'answer': 'A programming language',
        }

        serializer = QuizQuestionSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('question_options', serializer.errors)


class QuizSerializerTests(TestCase):
    """Tests serialization of quizzes and their questions."""

    def setUp(self):
        """Create a quiz with one question for serialization tests."""

        self.user = User.objects.create_user(
            username='testuser',
            password='Testpassword123!',
        )
        self.quiz = Quiz.objects.create(
            user=self.user,
            title='Test Quiz',
            description='Test description',
            video_url='https://www.youtube.com/watch?v=test123',
        )
        QuizQuestion.objects.create(
            quiz=self.quiz,
            question_title='What is Python?',
            question_options=[
                'A programming language',
                'A database',
                'A browser',
                'An operating system',
            ],
            answer='A programming language',
        )

    def test_quiz_contains_questions(self):
        """Verify serialized quiz data includes its questions."""

        serializer = QuizSerializer(self.quiz)

        self.assertEqual(
            len(serializer.data['questions']),
            1,
        )

        self.assertEqual(
            serializer.data['questions'][0]['question_title'],
            'What is Python?',
        )
