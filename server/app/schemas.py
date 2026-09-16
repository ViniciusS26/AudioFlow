from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AudioRecord(BaseModel):
    id: str
    original_name: str
    original_ext: str
    mime_type: str
    size_bytes: int
    duration_sec: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    bitrate: Optional[int] = None
    processing_type: str
    created_at: datetime
    path_original: str
    path_processed: Optional[str] = None
    waveform_url: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class UploadResponse(BaseModel):
    id: str
    message: str
    audio: AudioRecord
