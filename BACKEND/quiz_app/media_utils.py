"""Utilities for downloading and transcribing YouTube videos."""

import os
import tempfile
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

import whisper
import yt_dlp



YOUTUBE_HOSTS = {
    'youtube.com',
    'www.youtube.com',
    'm.youtube.com',
    'music.youtube.com',
    'youtu.be',
}

def validate_youtube_url(url):
    """Accept URLs from supported YouTube domains only."""
    if not isinstance(url, str) or not url.strip():
        raise ValueError("Eine YouTube-URL ist erforderlich.")
    parsed_url = urlparse(url.strip())
    if parsed_url.scheme not in {'http', 'https'}:
        raise ValueError("Die URL mus HTTP oder HTTPS verwenden.")
    if parsed_url.hostname not in YOUTUBE_HOSTS:
        raise ValueError("Es sind nur YouTube-URLs erlaubt.")
    return url.strip()

def _build_download_options(output_dir):
    """Build yt-dlp options for MP3 audio extraction."""
    return {
        'format': 'bestaudio/best',
        'outtmpl': str(Path(output_dir) / "%(id)s.%(ext)s"),
        'noplaylist': True,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

def _download_audio(url, output_dir):
    """Download and convert a video's audio to MP3."""
    options = _build_download_options(output_dir)
    with yt_dlp.YoutubeDL(options) as downloader:
        info = downloader.extract_info(url, download=True)
    audio_path = Path(output_dir) / f"{info['id']}.mp3"
    if not audio_path.is_file():
        raise RuntimeError("Die Audiodatei wurde nicht erstellt.")
    return audio_path, info.get('title', 'YouTube-Video')


@lru_cache(maxsize=1)
def _load_whisper_model():
    """Load and cache the configured Whisper model."""
    model_name = os.getenv('WHISPER_MODEL', 'base')
    return whisper.load_model(model_name)


def transcribe_youtube_video(url):
    """Download a YouTube video and return its title and transcript."""
    validated_url = validate_youtube_url(url)
    with tempfile.TemporaryDirectory() as temp_dir:
        audio_path, title = _download_audio(validated_url, temp_dir)
        result = _load_whisper_model().transcribe(str(audio_path))
        transcript = result.get('text', "").strip()
        if not transcript:
            raise ValueError("Whisper hat keinen Text erkannt.")
        return title, transcript
