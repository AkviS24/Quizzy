
# Quizzy

Quizzy is a web-based quiz application that enables users to generate, manage, and access quizzes based on YouTube videos. The backend provides a REST API for user authentication, automated quiz generation, and quiz management.

The project consists of a Django backend and a separately maintained frontend provided by the Developer Akademie Backendkurs.

## Table of Contents

- [Frontend](#frontend)
- [Features](#features)
  - [User authentication](#user-authentication)
  - [Quiz management](#quiz-management)
  - [Automatic quiz generation](#automatic-quiz-generation)
  - [Django Admin](#django-admin)
- [Technology Stack](#technology-stack)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Clone the repository](#1-clone-the-repository)
  - [Set up the backend](#2-set-up-the-backend)
  - [Configure environment variables](#3-configure-environment-variables)
  - [Prepare the database](#4-prepare-the-database)
  - [Start the development server](#5-start-the-development-server)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
  - [Authentication](#authentication)
  - [Quizzes](#quizzes)
- [Database Models](#database-models)
- [Development and Code Quality](#development-and-code-quality)
- [Testing](#testing)
- [Configuration and Security Notes](#configuration-and-security-notes)

## Frontend

The frontend repository is available at:

https://github.com/Developer-Akademie-Backendkurs/project.Quizly

The frontend communicates with the backend through its REST API.

## Features

### User authentication
- User registration with username, email, password, and password confirmation.
- User login with credential validation.
- JWT-based authentication using HTTP-only cookies for access and refresh tokens.
- Access-token refresh using the refresh token cookie.
- Logout with authentication-cookie deletion and token revocation.

### Quiz management
- Create quizzes from YouTube video URLs.
- Retrieve the authenticated user's quiz collection.
- Retrieve an individual quiz, including its questions and answer options.
- Update a quiz's title and description.
- Delete quizzes.
- Restrict quiz access and modifications to the quiz owner.
- Store quiz questions and their answer options in the database.

### Automatic quiz generation
The backend processes YouTube videos and generates multiple-choice quizzes through the following pipeline:

1. Retrieve video information and audio using `yt-dlp`.
2. Extract and convert audio using FFmpeg.
3. Transcribe the audio locally using OpenAI Whisper.
4. Send the transcript to Google Gemini Flash for quiz generation.
5. Validate the generated quiz data.
6. Save the quiz and its questions to the database.

Generated quizzes contain exactly 10 multiple-choice questions, each with four distinct answer options and one correct answer. The generated questions use the transcript's language, and the prompt instructs the model not to introduce facts unsupported by the transcript.

### Django Admin
The Django Admin interface supports managing quizzes and individual quiz questions, including searching and filtering records.

## Technology Stack

- **Python** — backend programming language
- **Django** — web framework
- **Django REST Framework** — REST API
- **Django REST Framework Simple JWT** — JWT authentication and refresh-token handling
- **SQLite** — default database
- **yt-dlp** — YouTube video information and audio retrieval
- **FFmpeg** — audio extraction and conversion
- **OpenAI Whisper** — speech transcription
- **PyTorch** — Whisper runtime
- **Google Gemini API** — automatic quiz generation
- **python-dotenv** — environment-variable configuration
- **Deno** — JavaScript runtime used by the current yt-dlp setup

## Requirements

Install the following software before setting up the backend:

- Python 3.14 or a compatible version for the pinned dependencies
- Git
- FFmpeg
- Deno

A Google Gemini API key is required for automatic quiz generation.

The Python dependencies are listed in `BACKEND/requirements.txt`.

The project currently pins `yt-dlp[default]` to version `2026.9.27.232945.dev0`. This development build was selected after the originally referenced version, `2025.07.21`, failed during testing with the YouTube Short used for development. Development builds can change or become unavailable, so this dependency should be reviewed before upgrading or deploying the application.

The development environment uses CPU-based PyTorch. Whisper transcription therefore runs on the CPU in that environment.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/AkviS24/Quizzy.git
cd Quizzy
```

### 2. Set up the backend

```bash
cd BACKEND
python -m venv .venv
```

Activate the virtual environment on Windows:

```cmd
.venv\Scripts\activate
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

From the `BACKEND` directory, copy the environment template to the repository root:

```cmd
copy ..\.env.example ..\.env
```

Open the newly created `.env` file in the repository root and replace the placeholder values with your own credentials:

- `SECRET_KEY`: A securely generated Django secret key.
- `GEMINI_API_KEY`: A valid Google Gemini API key.
- `DEBUG=True`: Enables debug mode for local development.

**Important:** Do not overwrite an existing `.env` file containing your actual credentials. Never commit `.env` or its secrets to version control.

### 4. Prepare the database

From the `BACKEND` directory, with the virtual environment activated, run:

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

The backend development server is available at:

http://127.0.0.1:8000/

The Django Admin interface is available at:

http://127.0.0.1:8000/admin/

Create a Django superuser to access the administration interface:

```bash
python manage.py createsuperuser
```

## Project Structure

```text
Quizzy/
├── BACKEND/
│   ├── core/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   ├── auth_app/
│   │   ├── api/
│   │   │   ├── serializers.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   ├── authentication.py
│   │   ├── functions.py
│   │   ├── models.py
│   │   └── tests/
│   ├── quiz_app/
│   │   ├── api/
│   │   │   ├── serializers.py
│   │   │   ├── urls.py
│   │   │   └── views.py
│   │   ├── media_utils.py
│   │   ├── functions.py
│   │   ├── utils.py
│   │   ├── models.py
│   │   ├── admin.py
│   │   └── tests/
│   ├── manage.py
│   ├── requirements.txt
│   └── .venv/
├── FRONTEND/
├── .env
├── .env.example
├── .gitignore
└── README.md
```

The virtual environment and local `.env` file are local development files and should not be committed. The frontend is maintained separately from the backend source code.

## API Reference

All API endpoints are prefixed with `/api/`.

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/register/` | Register a user. |
| `POST` | `/api/login/` | Authenticate a user and set authentication cookies. |
| `POST` | `/api/token/refresh/` | Refresh the access token using the refresh-token cookie. |
| `POST` | `/api/logout/` | Log out an authenticated user, revoke tokens, and clear authentication cookies. |

#### Registration

`POST /api/register/`

Request body:

```json
{
  "username": "example_user",
  "email": "user@example.com",
  "password": "your-password",
  "confirmed_password": "your-password"
}
```

A successful registration returns HTTP `201 Created`. Invalid input, a duplicate email address, or mismatched passwords result in a validation error.

#### Login

`POST /api/login/`

Request body:

```json
{
  "username": "example_user",
  "password": "your-password"
}
```

A successful login returns user information and sets HTTP-only access and refresh cookies.

#### Token refresh

`POST /api/token/refresh/`

The refresh token is read from the `refresh_token` cookie. On success, a new access token is set in the `access_token` cookie.

#### Troubleshooting: Expired or invalid token

The frontend normally attempts to refresh an expired access token automatically by calling `POST /api/token/refresh/`. If the refresh succeeds, the original request is retried.

If authentication still fails with an error such as `Token is expired` or `token_not_valid`, the browser may be holding expired or revoked authentication cookies.

For local development, recover the session as follows:

1. Open the frontend in the browser.
2. Open the browser developer tools with `F12`.
3. Go to **Application** and select **Storage**.
4. Use **Clear site data** to remove the stored data for the current frontend origin.
5. Reload the login page and sign in again with the existing username and password.

A successful login creates new HTTP-only `access_token` and `refresh_token` cookies. There is no need to register a new user.

**Note:** Clearing site data signs you out and removes other stored data for that origin. Use this only as a troubleshooting step. A normal logout intentionally revokes the current tokens.

#### Logout

`POST /api/logout/`

Requires an authenticated request. The backend revokes the access token, blacklists the refresh token when present, and deletes the authentication cookies.

### Quizzes

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/quizzes/` | Generate and create a quiz from a YouTube URL. |
| `GET` | `/api/quizzes/` | Retrieve the authenticated user's quizzes. |
| `GET` | `/api/quizzes/{id}/` | Retrieve a quiz, including its questions. |
| `PATCH` | `/api/quizzes/{id}/` | Partially update a quiz's title and/or description. |
| `DELETE` | `/api/quizzes/{id}/` | Delete a quiz. |

All quiz endpoints require authentication. Users can access and modify only their own quizzes. Requests for another user's quiz are denied; requests for a nonexistent quiz return a not-found response.

#### Create a quiz

`POST /api/quizzes/`

Request body:

```json
{
  "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

The backend retrieves and transcribes the video's audio, requests a quiz from Gemini, validates the generated data, and stores the quiz and its questions. If video processing or generation fails, the API returns an error response rather than saving an incomplete generated quiz.

#### Retrieve quizzes

`GET /api/quizzes/`

Returns the quizzes belonging to the authenticated user.

`GET /api/quizzes/{id}/`

Returns the selected quiz, including its associated questions, answer options, and correct answers.

#### Update a quiz

`PATCH /api/quizzes/{id}/`

Only the title and description are editable through this endpoint. The associated video URL cannot be changed through the update operation.

Example request:

```json
{
  "title": "Updated quiz title",
  "description": "Updated quiz description"
}
```

#### Delete a quiz

`DELETE /api/quizzes/{id}/`

Deletes the selected quiz. Its associated questions are deleted through the model relationship.

## Database Models

### Quiz

A quiz stores:

- The owning user
- The title and description
- The source YouTube URL
- Creation and update timestamps

### QuizQuestion

Each question belongs to a quiz and stores:

- The question text
- Four answer options
- The correct answer
- Creation and update timestamps

Deleting a quiz also deletes its associated questions.

## Development and Code Quality

The backend follows the project's clean-code requirements:

- Keep functions focused on one responsibility.
- Keep functions to a maximum of 14 lines where required by the project guidelines.
- Use descriptive names and `snake_case` for Python identifiers.
- Remove unused code and commented-out code.
- Provide meaningful docstrings and documentation.
- Keep HTTP request and response handling in API views.
- Place reusable business logic in helper modules such as `functions.py` and `utils.py`.
- Follow PEP 8 and established Django conventions.
- Keep quiz and question administration available through Django Admin.

## Testing

Run the backend test suite from the `BACKEND` directory with the virtual environment activated:

```bash
python manage.py test
```

Check the Django project configuration with:

```bash
python manage.py check
```

Tests cover authentication and token handling, registration validation, quiz API operations, ownership restrictions, and quiz data validation.

## Configuration and Security Notes

- Keep secret values in `.env`, not in source code.
- Do not commit `.env` or other files containing credentials.
- Keep `DEBUG=False` in production and configure `ALLOWED_HOSTS` appropriately before deployment.
- Use HTTPS in production and configure secure cookie settings for the deployment environment.
- Keep dependencies and external tools up to date, while testing compatibility before changing pinned versions.
