import hashlib
import json
import os
import shutil
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

from PIL import Image

from server.app.config import settings


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def ensure_storage_dirs() -> Path:
    base = Path(settings.STORAGE_DIR)
    base.mkdir(parents=True, exist_ok=True)
    trash = base / 'trash'
    trash.mkdir(exist_ok=True)
    return base


def build_audio_paths(audio_id: str, original_ext: str):
    today = datetime.utcnow()
    root = ensure_storage_dirs() / str(today.year) / f"{today.month:02d}" / f"{today.day:02d}" / audio_id
    root.mkdir(parents=True, exist_ok=True)
    original_path = root / f"audio.{original_ext.lower()}"
    processed_path = root / f"audio_processed.{original_ext.lower()}"
    waveform_path = root / 'waveform.png'
    meta_path = root / 'meta.json'
    return root, original_path, processed_path, waveform_path, meta_path


def generate_waveform(input_audio: str | Path, waveform_path: str | Path) -> None:
    out = Path(waveform_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new('RGB', (800, 200), 'white')
    try:
        import wave
        with wave.open(str(input_audio), 'rb') as wav:
            frames = wav.readframes(wav.getnframes())
            import struct
            values = [struct.unpack('<h', frames[i:i+2])[0] for i in range(0, len(frames), 2)]
            max_val = max(1, max(abs(v) for v in values))
            width = img.width
            step = max(1, len(values) // width)
            draw = img.load()
            for x in range(width):
                chunk = values[x*step:(x+1)*step]
                if not chunk:
                    continue
                avg = sum(abs(v) for v in chunk) / len(chunk)
                height = int((avg / max_val) * (img.height - 10))
                y0 = (img.height // 2) - height//2
                y1 = (img.height // 2) + height//2
                for y in range(y0, y1):
                    if 0 <= y < img.height:
                        draw[x, y] = (0, 0, 0)
            img.save(out)
    except Exception:
        img = Image.new('RGB', (800, 200), 'white')
        img.save(out)


def process_audio(file_path: str | Path, processing_type: str, output_path: str | Path) -> None:
    src = str(file_path)
    dst = str(output_path)
    if processing_type == 'normalize':
        subprocess.run(['ffmpeg', '-y', '-i', src, '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', dst], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif processing_type == 'mono':
        subprocess.run(['ffmpeg', '-y', '-i', src, '-ac', '1', dst], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif processing_type == 'speed':
        subprocess.run(['ffmpeg', '-y', '-i', src, '-filter:a', 'atempo=1.25', dst], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif processing_type == 'bitrate':
        subprocess.run(['ffmpeg', '-y', '-i', src, '-b:a', '96k', dst], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif processing_type == 'format':
        subprocess.run(['ffmpeg', '-y', '-i', src, '-c:a', 'pcm_s16le', dst], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        shutil.copyfile(src, dst)


def get_audio_metadata(path: str | Path) -> dict:
    import json
    result = subprocess.run([
        'ffprobe', '-v', 'error', '-show_entries', 'format=duration,bit_rate:stream=sample_rate,channels,codec_name',
        '-of', 'json', str(path)
    ], capture_output=True, text=True, check=True)
    payload = json.loads(result.stdout)
    stream = payload.get('streams', [{}])[0]
    fmt = payload.get('format', {})
    return {
        'duration_sec': float(fmt.get('duration', 0) or 0),
        'sample_rate': int(stream.get('sample_rate', 0) or 0),
        'channels': int(stream.get('channels', 0) or 0),
        'bitrate': int(fmt.get('bit_rate', 0) or 0),
        'mime_type': 'audio/' + (Path(str(path)).suffix.lower().lstrip('.'))
    }


def save_meta_file(meta_path: str | Path, payload: dict) -> None:
    with open(meta_path, 'w', encoding='utf-8') as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
