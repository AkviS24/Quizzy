# Quizzy

Quizzy is a web-based quiz application that allows users to create, manage and play quizzes.

The project consists of a separate backend and frontend. The backend provides a REST API and handles authentication, quiz management, quiz generation and the storage of quiz data.

The frontend is provided as a separate repository by the Developer Akademie Backendkurs.

## Frontend

The Quizzy frontend is available in the following repository:

https://github.com/Developer-Akademie-Backendkurs/project.Quizly

The frontend communicates with the Quizzy backend through the REST API.

## Installation

### Requirements

Before installing Quizzy, make sure the following software is installed:

- Python 3.14+
- FFmpeg
- Git
- Deno (JavaScript runtime required by the current yt-dlp setup)

The backend uses a Python virtual environment to keep its dependencies isolated from the system installation.

### External tools

#### FFmpeg

FFmpeg is used to extract and convert audio from downloaded YouTube videos. It must be installed separately and available on the system `PATH`.

Verify the installation with:

    ffmpeg -version

#### Deno

The current yt-dlp setup uses Deno to execute the JavaScript components required for YouTube extraction. Install Deno separately and ensure the executable is accessible to the backend process.

Verify the installation with:

    deno --version

If Deno is installed but the command is not recognized, its installation directory must be added to the Windows `PATH`, or the backend must be configured with the full path to the executable.

#### yt-dlp version note

The project specification originally referenced yt-dlp version `2025.07.21`. That version failed during testing with the YouTube Short used for development. The newer development build currently pinned in `BACKEND/requirements.txt` successfully retrieved the video's title and extracted its audio.

The currently tested version is `2026.9.27.232945.dev0`. This is an intentional, tested deviation from the original version reference. Development builds may change or become unavailable, so the pinned version should be re-evaluated before upgrading or deploying the application.

### Clone the repository

Clone the repository and navigate into the project directory:

    git clone <repository-url>
    cd Quizzy

### Set up the backend

Navigate to the backend directory:

    cd BACKEND

Create and activate the virtual environment:

    python -m venv .venv
    .venv\Scripts\activate

Install the Python dependencies:

    python -m pip install -r requirements.txt

### Environment variables

Create a `.env` file in the project root based on `.env.example`.

The `.env` file contains local configuration and secret values and must not be committed to the repository.

### Database

Initialize the Django database:

    python manage.py migrate

### Start the development server

Start the Django development server:

    python manage.py runserver

The backend is then available at:

    http://127.0.0.1:8000/

## Requirements

The backend dependencies are listed in:

    BACKEND/requirements.txt

Install or update them with:

    python -m pip install -r requirements.txt

The requirements file contains the Python dependencies. External programs such as FFmpeg and Deno must be installed separately.

The media-processing dependencies currently include:

- `yt-dlp[default]` for retrieving YouTube video information and downloading audio
- `openai-whisper` for local speech transcription
- `torch` for running Whisper
- FFmpeg for audio extraction and conversion
- Deno for the JavaScript runtime required by the current yt-dlp setup

The current development environment uses PyTorch `2.14.1+cpu`. CUDA is not available in this environment, so Whisper runs on the CPU. Transcription speed and quality depend on the selected Whisper model and the source audio.

## Project Structure

    Quizzy/
    ├── BACKEND/
    │   ├── .venv/
    │   ├── manage.py
    │   ├── requirements.txt
    │   └── core/
    │       ├── __init__.py
    │       ├── settings.py
    │       ├── urls.py
    │       ├── asgi.py
    │       └── wsgi.py
    ├── FRONTEND/
    ├── .env
    ├── .env.example
    ├── .gitignore
    └── README.md

## Configuration

Quizzy uses environment variables for local configuration and sensitive values.

The following variables are currently required:

    SECRET_KEY=your-secret-key-here
    DEBUG=True

The actual `.env` file is excluded from version control.

Additional environment variables may be required when external services, such as Google Gemini, are integrated.

## Planned Functionality

- User registration
- User login and logout
- JWT token refresh
- Quiz creation
- Quiz overview
- Quiz detail view
- Quiz editing
- Quiz deletion
- Quiz playback
- Automatic saving of quiz progress
- Quiz evaluation and results
- Sidebar with quizzes from today and the last 7 days
- Quiz generation from YouTube videos
- Automatic transcription using Whisper
- Automatic question generation using Google Gemini Flash
- Django Admin interface for managing quizzes and individual quiz questions
- Legal pages

## Quiz Generation

The planned quiz generation pipeline consists of the following steps:

1. A user provides a YouTube URL.
2. The video information and audio are retrieved using `yt-dlp`.
3. FFmpeg extracts and converts the audio into a format suitable for transcription.
4. The audio is transcribed locally using OpenAI Whisper.
5. The transcription is processed using Google Gemini Flash.
6. Gemini generates a quiz containing 10 questions with 4 answer options each.
7. The generated quiz is stored in the backend.

The YouTube audio extraction and local Whisper transcription steps have been tested with a YouTube Short. The complete automatic quiz generation pipeline, including Gemini integration and end-to-end testing, still needs to be completed.

## API

The backend provides a REST API for communication with the frontend.

### Authentication

The authentication API includes:

- `POST /api/register/`
- `POST /api/login/`
- `POST /api/logout/`
- `POST /api/token/refresh/`

Authentication uses JWT tokens. Access and refresh tokens are handled through HTTP-only cookies.

### Quizzes

The quiz API includes:

- `POST /api/quizzes/`
- `GET /api/quizzes/`
- `GET /api/quizzes/{id}/`
- `PATCH /api/quizzes/{id}/`
- `DELETE /api/quizzes/{id}/`

## Technology

The backend is built with:

- Python
- Django
- Django REST Framework
- yt-dlp
- FFmpeg
- OpenAI Whisper
- PyTorch
- Google Gemini Flash
- Deno for the JavaScript runtime required by the current yt-dlp setup

The frontend is provided separately and communicates with the backend through the REST API.

## Development

The project is developed incrementally with a focus on clean and maintainable code.

Changes should be organized into small, meaningful and thematically separated Git commits.

Before committing changes, the project should be tested to ensure that the current development state remains functional.

The backend follows clean-code principles, including:

- Functions should generally not exceed 14 lines.
- Each function should perform one clearly defined task.
- Use meaningful variable and function names.
- Use `snake_case` for Python identifiers.
- Remove unused variables and functions.
- Remove commented-out code.
- Add meaningful documentation and docstrings where appropriate.
- Keep Django responsibilities in their appropriate files.
- Keep views focused on handling HTTP requests and returning responses.
- Use helper modules such as `functions.py` or `utils.py` for reusable functionality.
- Maintain the Django Admin interface for managing quizzes and individual quiz questions.
- Follow PEP 8 and Pythonic coding practices.