"""
Transcription service — Groq Whisper Large V3.
Handles the 25MB file size limit via ffmpeg chunking.
"""
import os
import math
import tempfile
import subprocess
from pathlib import Path
from app.settings import settings

MAX_CHUNK_MB = 24  # stay under Groq's 25MB limit
MAX_CHUNK_BYTES = MAX_CHUNK_MB * 1024 * 1024


async def transcribe_file(file_path: str) -> str:
    """
    Transcribe an audio/video file. Chunks automatically if > 24MB.
    Returns the full transcript as a single string.
    """
    path = Path(file_path)
    if path.stat().st_size <= MAX_CHUNK_BYTES:
        return await _transcribe_chunk(file_path)

    chunks = _split_audio(file_path)
    try:
        parts = []
        for chunk in chunks:
            parts.append(await _transcribe_chunk(chunk))
        return "\n".join(parts)
    finally:
        for chunk in chunks:
            try:
                os.unlink(chunk)
            except OSError:
                pass


async def transcribe_url(url: str) -> str:
    """Download audio from URL (yt-dlp), then transcribe."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, "audio.%(ext)s")
        subprocess.run(
            ["yt-dlp", "-x", "--audio-format", "mp3", "-o", output_path, url],
            check=True,
            capture_output=True,
        )
        # Find the downloaded file
        files = list(Path(tmpdir).glob("audio.*"))
        if not files:
            raise RuntimeError(f"yt-dlp produced no output for {url}")
        return await transcribe_file(str(files[0]))


def _split_audio(file_path: str) -> list[str]:
    """Split audio into chunks using ffmpeg. Returns list of temp file paths."""
    # Probe duration
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", file_path],
        capture_output=True,
        text=True,
        check=True,
    )
    import json
    info = json.loads(result.stdout)
    duration = float(info["format"]["duration"])
    file_size = Path(file_path).stat().st_size
    num_chunks = math.ceil(file_size / MAX_CHUNK_BYTES)
    chunk_duration = duration / num_chunks

    chunks = []
    for i in range(num_chunks):
        start = i * chunk_duration
        fd, chunk_path = tempfile.mkstemp(suffix=".mp3")
        os.close(fd)
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", file_path,
                "-ss", str(start), "-t", str(chunk_duration),
                "-acodec", "mp3", chunk_path,
            ],
            check=True,
            capture_output=True,
        )
        chunks.append(chunk_path)
    return chunks


async def _transcribe_chunk(file_path: str) -> str:
    from groq import Groq
    client = Groq(api_key=settings.GROQ_API_KEY)
    with open(file_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=f,
        )
    return response.text
