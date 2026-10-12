"""Tests for YouTube media utilities."""

import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import MagicMock, patch

from quiz_app.media_utils import (
    _download_audio,
    _load_whisper_model,
    transcribe_youtube_video,
    validate_youtube_url,
)


class ValidateYouTubeURLTests(TestCase):
    """Test validation of supported YouTube URLs."""

    def test_accepts_standard_youtube_url(self):
        """Accept a standard YouTube watch URL."""

        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertEqual(validate_youtube_url(url), url)

    def test_accepts_short_youtube_url(self):
        """Normalize a shortened YouTube URL."""

        url = "https://youtu.be/dQw4w9WgXcQ"
        expected = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        self.assertEqual(validate_youtube_url(url), expected)

    def test_normalizes_youtube_shorts_url(self):
        """Normalize Shorts URLs for the supplied frontend."""
        url = "https://www.youtube.com/shorts/63ISYh7IV-s"
        expected = "https://www.youtube.com/watch?v=63ISYh7IV-s"

        self.assertEqual(validate_youtube_url(url), expected)

    def test_rejects_external_domain(self):
        """Reject URLs from domains other than YouTube."""

        with self.assertRaises(ValueError):
            validate_youtube_url("https://example.com/video")

    def test_rejects_unsupported_scheme(self):
        """Reject YouTube URLs that use an unsupported scheme."""

        with self.assertRaises(ValueError):
            validate_youtube_url("ftp://youtube.com/video")

    def test_rejects_empty_url(self):
        """Reject an empty video URL."""

        with self.assertRaises(ValueError):
            validate_youtube_url("")


class DownloadAudioTests(TestCase):
    """Test audio downloading without network access."""

    def test_downloads_audio_and_returns_video_title(self):
        """Verify audio download output and extracted video title."""
        with tempfile.TemporaryDirectory() as output_dir:
            audio_path = Path(output_dir) / "video123.mp3"
            downloader = MagicMock()

            def create_audio(*args, **kwargs):
                """Create a mock audio file and return video metadata."""
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

    def test_missing_audio_file_raises_error(self):
        """Raise an error when the downloaded audio file is missing."""
        with tempfile.TemporaryDirectory() as output_dir:
            downloader = MagicMock()
            downloader.extract_info.return_value = {
                "id": "video123",
                "title": "Testvideo",
            }

            with patch(
                "quiz_app.media_utils.yt_dlp.YoutubeDL",
                return_value=downloader,
            ):
                downloader.__enter__.return_value = downloader
                with self.assertRaisesRegex(
                    RuntimeError,
                    "Die Audiodatei wurde nicht erstellt.",
                ):
                    _download_audio(
                        "https://youtu.be/video123",
                        output_dir,
                    )


class TranscriptionTests(TestCase):
    """Test transcription without loading Whisper."""

    @patch("quiz_app.media_utils.whisper.load_model")
    def test_loads_configured_whisper_model(self, mock_load_model):
        """Load and cache the model selected by configuration."""
        _load_whisper_model.cache_clear()
        self.addCleanup(_load_whisper_model.cache_clear)

        with patch.dict("os.environ", {"WHISPER_MODEL": "tiny"}):
            model = _load_whisper_model()
            cached_model = _load_whisper_model()

        self.assertIs(model, mock_load_model.return_value)
        self.assertIs(cached_model, model)
        mock_load_model.assert_called_once_with("tiny")

    @patch("quiz_app.media_utils._load_whisper_model")
    @patch("quiz_app.media_utils._download_audio")
    def test_transcribes_audio_and_strips_whitespace(
        self,
        mock_download,
        mock_load_model,
    ):
        """Return the transcription with surrounding whitespace removed."""

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
        """Reject transcriptions that contain only whitespace."""

        mock_download.return_value = (Path("audio.mp3"), "Testvideo")
        mock_load_model.return_value.transcribe.return_value = {
            "text": "   "
        }

        with self.assertRaises(ValueError):
            transcribe_youtube_video(
                "https://youtu.be/dQw4w9WgXcQ"
            )
