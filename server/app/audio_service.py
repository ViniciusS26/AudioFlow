import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from server.app.config import settings
from server.app.models import Audio
from server.app.storage import (
    generate_waveform,
    get_audio_metadata,
    process_audio,
    save_meta_file,
    sha256_file,
)


VALID_PROCESSINGS = {'normalize', 'mono', 'speed', 'bitrate', 'format', 'original'}


def ensure_valid_processing(value: str) -> str:
    normalized = (value or 'original').strip().lower()
    if normalized not in VALID_PROCESSINGS:
        raise ValueError(f"Processamento inválido: {value}")
    return normalized


def save_uploaded_audio(db: Session, upload: UploadFile, processing_type: str) -> Audio:
    processing_type = ensure_valid_processing(processing_type)
    audio_id = str(uuid4())
    original_ext = Path(upload.filename or 'audio.wav').suffix.lower().lstrip('.') or 'wav'
    storage_root = settings.STORAGE_DIR / str(datetime.utcnow().year) / f"{datetime.utcnow().month:02d}" / f"{datetime.utcnow().day:02d}" / audio_id
    storage_root.mkdir(parents=True, exist_ok=True)

    original_path = storage_root / f"audio.{original_ext}"
    processed_path = storage_root / f"audio_processed.{original_ext}"
    waveform_path = storage_root / 'waveform.png'
    meta_path = storage_root / 'meta.json'

    with open(original_path, 'wb') as f:
        shutil.copyfileobj(upload.file, f)

    process_audio(original_path, processing_type, processed_path)
    generate_waveform(original_path, waveform_path)

    metadata = get_audio_metadata(original_path)
    checksum = sha256_file(original_path)
    meta = {
        'id': audio_id,
        'original_name': upload.filename,
        'checksum': checksum,
        'processing_type': processing_type,
        'size_bytes': os.path.getsize(original_path),
        'duration_sec': metadata['duration_sec'],
        'sample_rate': metadata['sample_rate'],
        'channels': metadata['channels'],
        'bitrate': metadata['bitrate'],
        'path_original': str(original_path),
        'path_processed': str(processed_path),
        'waveform_png': str(waveform_path),
        'created_at': datetime.utcnow().isoformat(),
    }
    save_meta_file(meta_path, meta)

    db_audio = Audio(
        id=audio_id,
        original_name=upload.filename or 'audio',
        original_ext=original_ext,
        mime_type=f'audio/{original_ext}' if original_ext else 'audio/wav',
        size_bytes=meta['size_bytes'],
        duration_sec=meta['duration_sec'],
        sample_rate=meta['sample_rate'],
        channels=meta['channels'],
        bitrate=meta['bitrate'],
        processing_type=processing_type,
        created_at=datetime.utcnow(),
        path_original=str(original_path),
        path_processed=str(processed_path),
    )
    db.add(db_audio)
    db.commit()
    db.refresh(db_audio)
    return db_audio


def list_audios(db: Session):
    return db.query(Audio).order_by(Audio.created_at.desc()).all()
