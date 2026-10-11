"""Utilities for generating quizzes with the Gemini API."""

import json
import os

from google import genai


QUIZ_PROMPT_TEMPLATE = """
Erstelle aus dem folgenden Transkript ein Quiz.
Erzeuge genau 10 Multiple-Choice-Fragen mit jeweils 4 Optionen.
Verwende die Sprache des Transkripts.
Erfinde keine Fakten, die nicht durch das Transkript gestützt sind.
Gib ausschließlich gültiges JSON in diesem Format zurück:
{
    "title": "Kurzer Quiztitel",
    "description": "Kurze Beschreibung",
    "questions": [
        {
            "question_title": "Frage",
            "question_options": ["A", "B", "C", "D"],
            "answer": "A"
        }
    ]
}
Transkript:
{transcript}
"""


def _build_quiz_prompt(transcript):
    """Build the prompt used to generate a quiz."""
    return QUIZ_PROMPT_TEMPLATE.replace("{transcript}", transcript)


def _validate_quiz(quiz):
    """Validate the structure and answers of a generated quiz."""
    if not isinstance(quiz, dict):
        raise ValueError("Das generierte Quiz muss ein Objekt sein.")
    _validate_quiz_metadata(quiz)
    _validate_quiz_questions(quiz.get("questions"))


def _validate_quiz_metadata(quiz):
    """Validate the title and description of a generated quiz."""
    _validate_quiz_title(quiz.get("title"))
    _validate_quiz_description(quiz.get("description"))


def _validate_quiz_title(title):
    """Ensure the generated quiz has a non-empty title."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Der Quiztitel fehlt oder ist ungültig.")


def _validate_quiz_description(description):
    """Ensure the generated quiz has a non-empty description."""
    if not isinstance(description, str) or not description.strip():
        raise ValueError("Die Quizbeschreibung fehlt oder ist ungültig.")


def _validate_quiz_questions(questions):
    """Validate the number and contents of generated questions."""
    if not isinstance(questions, list) or len(questions) != 10:
        raise ValueError("Gemini muss genau 10 Fragen erzeugen.")
    for question in questions:
        _validate_question(question)


def _validate_question(question):
    """Validate one question and its answer options."""
    if not isinstance(question, dict):
        raise ValueError("Jede Frage muss ein Objekt sein.")
    _validate_question_title(question.get("question_title"))
    options = question.get("question_options")
    _validate_question_options(options)
    _validate_correct_answer(question.get("answer"), options)


def _validate_question_title(title):
    """Ensure a question has a non-empty title."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Der Fragetext fehlt oder ist ungültig.")


def _validate_question_options(options):
    """Validate four non-empty, distinct answer options."""
    if not isinstance(options, list) or len(options) != 4:
        raise ValueError("Jede Frage benötigt genau 4 Optionen.")
    if not all(isinstance(option, str) and option.strip() for option in options):
        raise ValueError("Alle Antworten müssen Text enthalten.")
    if len(set(options)) != len(options):
        raise ValueError("Die Antwortoptionen müssen eindeutig sein.")


def _validate_correct_answer(answer, options):
    """Ensure the correct answer matches one of the available options."""
    if not isinstance(answer, str) or answer not in options:
        raise ValueError("Die richtige Antwort muss eine der Optionen sein.")


def _create_gemini_client():
    """Create a Gemini client using the configured API key."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Der Gemini API-Key fehlt.")
    return genai.Client(api_key=api_key)


def _request_quiz_generation(client, transcript):
    """Request a structured quiz from Gemini."""
    return client.models.generate_content(
        model="gemini-flash-latest",
        contents=_build_quiz_prompt(transcript),
        config={"response_mime_type": "application/json"},
    )


def _parse_generated_quiz(response):
    """Parse and validate Gemini's response."""
    if not response or not response.text or not response.text.strip():
        raise ValueError(
            "Gemini hat keine gültige Textantwort zurückgegeben."
        )
    quiz = json.loads(response.text)
    _validate_quiz(quiz)
    return quiz


def generate_quiz_from_transcript(transcript):
    """Generate and validate a quiz from a transcript."""
    if not isinstance(transcript, str) or not transcript.strip():
        raise ValueError("Das Transkript muss ein nicht leerer Text sein.")
    client = _create_gemini_client()
    response = _request_quiz_generation(client, transcript)
    return _parse_generated_quiz(response)
