from __future__ import annotations

import os
import uuid as uuid_module
from pathlib import Path
from urllib.parse import urlencode

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from server.app.audio_service import list_audios, save_uploaded_audio
from server.app.database import SessionLocal, init_db
from server.app.models import Audio
from server.app.schemas import AudioRecord, UploadResponse

app = FastAPI(title=os.getenv("APP_TITLE", "Audio Processing API"))
API_TOKEN = os.getenv("API_TOKEN", "audio-demo-token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_api_key(
    request: Request,
    authorization: str | None = Header(default=None),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    if not API_TOKEN:
        return True

    query_token = request.query_params.get("token") or request.query_params.get("api_key")
    received = query_token

    if not received and authorization:
        pieces = authorization.split()
        if len(pieces) == 2 and pieces[0].lower() == "bearer":
            received = pieces[1]
    if not received and x_api_key:
        received = x_api_key

    if received != API_TOKEN:
        raise HTTPException(status_code=401, detail="Token de autenticação inválido ou ausente.")
    return True


@app.on_event("startup")
def startup():
    init_db()


@app.get("/", response_class=HTMLResponse)
def index():
    rows = []
    with SessionLocal() as db:
        for item in list_audios(db):
            original_name = Path(item.path_original).name
            processed_name = Path(item.path_processed).name if item.path_processed else ''
            original_params = urlencode({'uuid': str(item.id), 'token': API_TOKEN})
            processed_params = urlencode({'uuid': str(item.id), 'token': API_TOKEN})
            processed_link = f" | <a href='/files/{processed_name}?{processed_params}'>Processado</a>" if processed_name else ''
            rows.append(
                f"<li><strong>{item.original_name}</strong> - {item.processing_type} - <a href='/files/{original_name}?{original_params}'>Original</a>{processed_link}</li>"
            )
    html = """
    <html>
      <head><title>Audio Archive</title></head>
      <body>
        <h1>Áudios armazenados</h1>
        <ul>
          {rows}
        </ul>
      </body>
    </html>
    """.format(rows=''.join(rows) if rows else '<li>Nenhum áudio encontrado.</li>')
    return HTMLResponse(content=html)


@app.get("/api/audios", response_model=list[AudioRecord])
def get_audios(db: Session = Depends(get_db), _: bool = Depends(require_api_key)):
    return list_audios(db)


@app.post("/api/upload", response_model=UploadResponse)
async def upload_audio(
    file: UploadFile = File(...),
    processing_type: str = Form('normalize'),
    db: Session = Depends(get_db),
    _: bool = Depends(require_api_key),
):
    try:
        audio = save_uploaded_audio(db, file, processing_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return UploadResponse(
        id=audio.id,
        message='Arquivo enviado e processado com sucesso.',
        audio=AudioRecord.model_validate(audio)
    )


@app.get("/files/{filename}")
def get_file(filename: str, uuid: str, db: Session = Depends(get_db), _: bool = Depends(require_api_key)):
    try:
        uuid_value = str(uuid_module.UUID(uuid))
    except (ValueError, TypeError):
        raise HTTPException(status_code=404, detail='Áudio não encontrado.') from None

    item = db.query(Audio).filter(Audio.id == uuid_value).first()
    if not item:
        raise HTTPException(status_code=404, detail='Áudio não encontrado.')

    file_path = Path(item.path_original)
    if filename != Path(item.path_original).name and filename != Path(item.path_processed).name:
        file_path = Path(item.path_processed) if item.path_processed else Path(item.path_original)
    else:
        file_path = Path(item.path_original) if filename == Path(item.path_original).name else Path(item.path_processed)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail='Arquivo não encontrado no disco.')
    return FileResponse(file_path)


@app.get("/waveform/{audio_id}")
def get_waveform(audio_id: str, db: Session = Depends(get_db), _: bool = Depends(require_api_key)):
    try:
        audio_id_value = str(uuid_module.UUID(audio_id))
    except (ValueError, TypeError):
        raise HTTPException(status_code=404, detail='Áudio não encontrado.') from None

    item = db.query(Audio).filter(Audio.id == audio_id_value).first()
    if not item:
        raise HTTPException(status_code=404, detail='Áudio não encontrado.')
    wave = Path(item.path_original).parent / 'waveform.png'
    if not wave.exists():
        raise HTTPException(status_code=404, detail='Waveform não encontrada.')
    return FileResponse(wave)
