import json
from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase

from quiz_app.utils import (
    _validate_question,
    _validate_quiz,
    generate_quiz_from_transcript,
)


def make_question():
    """Create a valid simple question."""
    return {
        'question_title': 'Was ist Python?',
        'question_options': [
            'Programmiersprache',
            'Datenbank',
            'Browser',
            'Betriebssystem',
        ],
        'answer': 'Programmiersprache',
    }


def make_quiz():
    """Create a valid simple quiz."""
    return {
        'title': 'Python Quiz',
        'description': 'Ein kurzes Quiz über Python.',
        'questions': [make_question() for _ in range(10)],
    }


class QuizValidationTest(SimpleTestCase):
    """Test validation of generated quiz data."""

    def test_valid_quiz_is_accepted(self):
        """Accept a quiz that satisfies all validation rules."""

        _validate_quiz(make_quiz())

    def test_quiz_with_nine_questions_is_rejected(self):
        """Reject a quiz containing only nine questions."""

        quiz = make_quiz()
        quiz['questions'].pop()

        with self.assertRaises(ValueError):
            _validate_quiz(quiz)

    def test_quiz_with_three_options_is_rejected(self):
        """Reject a question containing fewer than four options."""

        question = make_question()
        question['question_options'].pop()

        with self.assertRaises(ValueError):
            _validate_question(question)

    def test_answer_not_in_options_is_rejected(self):
        """Reject an answer that is absent from the available options."""

        question = make_question()
        question['answer'] = 'Keine der Optionen.'

        with self.assertRaises(ValueError):
            _validate_question(question)

    def test_empty_option_is_rejected(self):
        """Reject a question containing an empty option."""

        question = make_question()
        question['question_options'][0] = ""

        with self.assertRaises(ValueError):
            _validate_question(question)

    def test_duplicate_options_are_rejected(self):
        """Reject a question with duplicate answer options."""

        question = make_question()
        question['question_options'] = [
            'Programmiersprache',
            'Programmiersprache',
            'Browser',
            'Betriebssystem',
        ]

        with self.assertRaises(ValueError):
            _validate_question(question)

    def test_none_quiz_is_rejected(self):
        """Reject a missing quiz value."""

        with self.assertRaises(ValueError):
            _validate_quiz(None)

    def test_missing_questions_are_rejected(self):
        """Reject quiz data without a questions field."""

        with self.assertRaises(ValueError):
            _validate_quiz({})

    def test_none_question_is_rejected(self):
        """Reject a missing question value."""

        with self.assertRaises(ValueError):
            _validate_question(None)

    def test_empty_question_title_is_rejected(self):
        """Reject a question with a blank title."""

        question = make_quiz()['questions'][0]
        question['question_title'] = "  "

        with self.assertRaises(ValueError):
            _validate_question(question)

    def test_empty_answer_option_is_rejected(self):
        """Reject question data containing a blank option value."""

        question = make_quiz()['questions'][0]
        question['question_options'][0] = ""

        with self.assertRaises(ValueError):
            _validate_question(question)

    def test_invalid_answer_type_is_rejected(self):
        """Reject an answer whose value is not a string."""

        question = make_quiz()['questions'][0]
        question['answer'] = None

        with self.assertRaises(ValueError):
            _validate_question(question)

    def test_quiz_with_too_few_questions_is_rejected(self):
        """Reject a quiz containing fewer than ten questions."""

        quiz = make_quiz()
        quiz['questions'] = quiz['questions'][:9]

        with self.assertRaises(ValueError):
            _validate_quiz(quiz)

    def test_quiz_with_too_many_questions_is_rejected(self):
        """Reject a quiz containing more than ten questions."""

        quiz = make_quiz()
        quiz['questions'].append(quiz['questions'][0].copy())

        with self.assertRaises(ValueError):
            _validate_quiz(quiz)

    def test_empty_quiz_title_is_rejected(self):
        """Reject quiz data with a blank title."""

        quiz = make_quiz()
        quiz['title'] = "  "

        with self.assertRaises(ValueError):
            _validate_quiz(quiz)

    def test_empty_quiz_description_is_rejected(self):
        """Reject quiz data with an empty description."""

        quiz = make_quiz()
        quiz['description'] = ""

        with self.assertRaises(ValueError):
            _validate_quiz(quiz)


class QuizGenerationTest(SimpleTestCase):
    """Test quiz generation without calling the real Gemini API."""

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'})
    @patch('quiz_app.utils.genai.Client')
    def test_generated_quiz_is_returned(self, client_class):
        """Return quiz data when Gemini provides valid JSON."""

        quiz = make_quiz()
        response = SimpleNamespace(text=json.dumps(quiz))
        client = Mock()
        client.models.generate_content.return_value = response
        client_class.return_value = client

        result = generate_quiz_from_transcript('Ein Python-Transkript.')

        self.assertEqual(result, quiz)
        client.models.generate_content.assert_called_once()

        self.assertEqual(
            client.models.generate_content.call_args.kwargs['model'],
            'gemini-flash-latest',
        )

    @patch('quiz_app.utils.genai.Client')
    def test_invalid_json_response_raises_error(self, mock_client):
        """Raise a JSON decoding error for an invalid response."""

        mock_client.return_value.models.generate_content.return_value.text = (
            "Das ist kein gültiges JSON."
        )

        with self.assertRaises(json.JSONDecodeError):
            generate_quiz_from_transcript('Ein Testtranskript.')

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'})
    @patch('quiz_app.utils.genai.Client')
    def test_empty_api_response_is_rejected(self, mock_client):
        """Reject an empty response from Gemini."""

        mock_client.return_value.models.generate_content.return_value = (
            SimpleNamespace(text='')
        )

        with self.assertRaisesMessage(
            ValueError,
            'Gemini hat keine gültige Textantwort zurückgegeben.',
        ):
            generate_quiz_from_transcript('Ein Testtranskript.')

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'})
    @patch('quiz_app.utils.genai.Client')
    def test_none_api_response_is_rejected(self, mock_client):
        """Reject a missing response from Gemini."""

        mock_client.return_value.models.generate_content.return_value = None

        with self.assertRaisesMessage(
            ValueError,
            'Gemini hat keine gültige Textantwort zurückgegeben.',
        ):
            generate_quiz_from_transcript('Ein Testtranskript.')

    @patch.dict('os.environ', {}, clear=True)
    def test_missing_api_key_is_rejected(self):
        """Reject quiz generation when the API key is missing."""

        with self.assertRaises(ValueError):
            generate_quiz_from_transcript('Ein Transkript.')

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'})
    def test_none_transcript_is_rejected(self):
        """Reject a missing transcript."""

        with self.assertRaises(ValueError):
            generate_quiz_from_transcript(None)

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'})
    def test_empty_transcript_is_rejected(self):
        """Reject an empty transcript."""

        with self.assertRaises(ValueError):
            generate_quiz_from_transcript("")

    @patch.dict('os.environ', {'GEMINI_API_KEY': 'test-key'})
    def test_whitespace_transcript_is_rejected(self):
        """Reject a transcript containing only whitespace."""

        with self.assertRaises(ValueError):
            generate_quiz_from_transcript("  ")
