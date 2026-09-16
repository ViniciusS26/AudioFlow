import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

ffmpeg_candidate = Path(os.getenv("FFMPEG_BIN", BASE_DIR / "tools" / "ffmpeg" / "ffmpeg-master-latest-win64-gpl" / "bin"))
if ffmpeg_candidate.exists() and str(ffmpeg_candidate) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{ffmpeg_candidate}{os.pathsep}{os.environ.get('PATH', '')}"


class Settings:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://audio_user:audio_pass@localhost:5432/audio_db",
    )
    STORAGE_DIR = Path(os.getenv("STORAGE_DIR", BASE_DIR / "server" / "storage"))
    APP_TITLE = os.getenv("APP_TITLE", "Audio Processing API")
    FFMPEG_BIN = ffmpeg_candidate
    API_TOKEN = os.getenv("API_TOKEN", "audio-demo-token")


settings = Settings()
