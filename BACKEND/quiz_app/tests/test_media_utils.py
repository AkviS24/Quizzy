"""Tests for YouTube media utilities."""

import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from quiz_app.media_utils import (
    _download_audio,
    transcribe_youtube_video,
    validate_youtube_url,
)


class ValidateYouTubeURLTests(TestCase):
    """Test validation of supported YouTube URLs."""

    def test_accepts_standard_youtube_url(self):
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertEqual(validate_youtube_url(url), url)

    def test_accepts_short_youtube_url(self):
        url = "https://youtu.be/dQw4w9WgXcQ"
        self.assertEqual(validate_youtube_url(url), url)

    def test_rejects_external_domain(self):
        with self.assertRaises(ValueError):
            validate_youtube_url("https://example.com/video")

    def test_rejects_unsupported_scheme(self):
        with self.assertRaises(ValueError):
            validate_youtube_url("ftp://youtube.com/video")

    def test_rejects_empty_url(self):
        with self.assertRaises(ValueError):
            validate_youtube_url("")


class DownloadAudioTests(TestCase):
    """Test audio downloading without network access."""

    def test_downloads_audio_and_returns_video_title(self):
        with tempfile.TemporaryDirectory() as output_dir:
            audio_path = Path(output_dir) / "video123.mp3"
            downloader = MagicMock()

            def create_audio(*args, **kwargs):
                audio_path.touch()
                return {"id": "video123", "title": "Testvideo"}

            downloader.extract_info.side_effect = create_audio

            with patch(
                "quiz_app.media_utils.yt_dlp.YoutubeDL",
                return_value=downloader,
            ):
                downloader.__enter__.return_value = downloader
                path, title = _download_audio(
                    "https://youtu.be/video123",
                    output_dir,
                )

            self.assertEqual(path, audio_path)
            self.assertEqual(title, "Testvideo")
            self.assertTrue(path.is_file())


class TranscriptionTests(TestCase):
    """Test transcription without loading Whisper."""

    @patch("quiz_app.media_utils._load_whisper_model")
    @patch("quiz_app.media_utils._download_audio")
    def test_transcribes_audio_and_strips_whitespace(
        self,
        mock_download,
        mock_load_model,
    ):
        mock_download.side_effect = lambda url, directory: (
            Path(directory) / "audio.mp3",
            "Testvideo",
        )
        model = mock_load_model.return_value
        model.transcribe.return_value = {"text": "  Hallo Welt  "}

        title, transcript = transcribe_youtube_video(
            "https://youtu.be/dQw4w9WgXcQ"
        )

        self.assertEqual(title, "Testvideo")
        self.assertEqual(transcript, "Hallo Welt")
        model.transcribe.assert_called_once()

    @patch("quiz_app.media_utils._load_whisper_model")
    @patch("quiz_app.media_utils._download_audio")
    def test_rejects_empty_transcript(
        self,
        mock_download,
        mock_load_model,
    ):
        mock_download.return_value = (Path("audio.mp3"), "Testvideo")
        mock_load_model.return_value.transcribe.return_value = {
            "text": "   "
        }

        with self.assertRaises(ValueError):
            transcribe_youtube_video(
                "https://youtu.be/dQw4w9WgXcQ"
            )
