"""Utilities for generating quizzes with the Gemini API."""

import json
import os

from google import genai


def _build_quiz_prompt(transcript):
    """Build the prompt for quiz generating."""
    return f"""
Erstelle aus dem folgenden Transkript ein Quiz.
Erzeuge genau 10 Multiple-Choice-Fragen mit jeweils 4 Optionen.
Verwende die Sprache des Transkripts.
Erfinde keine Fakten, die nicht durch das Transkript gestützt sind.
Gib ausschließlich gültiges JSON in diesem Format zurück:
{{
    "title": "Kurzer Quiztitel",
    "description": "Kurze Beschreibung",
    "questions": [
        {{
        "question_title": "Frage",
        "question_options": ["A", "B", "C", "D"],
        "answer": "A"
        }}
    ]
}}
Transkript:
{transcript}
"""


def _validate_quiz(quiz):
    """Validate the structure and answers of a generated quiz."""
    if not isinstance(quiz, dict):
        raise ValueError("Das generierte Quiz muss ein Objekt sein.")

    title = quiz.get('title')
    description = quiz.get('description')

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Der Quiztitel fehlt oder ist ungültig.")

    if not isinstance(description, str) or not description.strip():
        raise ValueError("Die Quizbeschreibung fehlt oder ist ungültig.")

    questions = quiz.get('questions')
    if not isinstance(questions, list) or len(questions) != 10:
        raise ValueError("Gemini muss genau 10 Fragen erzeugen.")

    for question in questions:
        _validate_question(question)


def _validate_question(question):
    """Validate one question and its answer options."""
    if not isinstance(question, dict):
        raise ValueError("Jede Frage muss ein Objekt sein.")

    title = question.get('question_title')
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Der Fragetext fehlt oder ist ungültig.")

    options = question.get('question_options')
    if not isinstance(options, list) or len(options) != 4:
        raise ValueError("Jede Frage benötigt genau 4 Optionen.")

    if not all(isinstance(option, str) and option.strip() for option in options):
        raise ValueError("Alle Antworten müssen Text enthalten.")

    if len(set(options)) != len(options):
        raise ValueError("Die Antwortoptionen müssen eindeutig sein.")

    answer = question.get('answer')
    if not isinstance(answer, str) or answer not in options:
        raise ValueError("Die richtige Antwort muss eine der Optionen sein.")


def generate_quiz_from_transcript(transcript):
    """Generate and validate a quiz from a transcript."""
    if not isinstance(transcript, str) or not transcript.strip():
        raise ValueError("Das Transkript muss ein nicht leerer Text sein.")

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("Der Gemini API-Key fehlt.")

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-flash-latest',
        contents=_build_quiz_prompt(transcript),
        config={'response_mime_type': 'application/json'},
    )

    if not response or not response.text or not response.text.strip():
        raise ValueError(
            "Gemini hat keine gültige Textantwort zurückgegeben."
        )

    quiz = json.loads(response.text)
    _validate_quiz(quiz)
    return quiz
