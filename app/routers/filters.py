import tempfile
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.routers.audio_http import wav_response
from app.services.filter import filter_single_band
from app.services.signal_utils import load_audio

router = APIRouter()


@router.post("/single-band")
async def single_band(
    file: Annotated[UploadFile, File()],
    center_freq: Annotated[float, Form(gt=0)],
    order: Annotated[int, Form(ge=1, le=10)] = 4,
):
    contenido = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp.write(contenido)
        ruta = Path(tmp.name)
    try:
        senal, fs = load_audio(ruta)
        filtrada = filter_single_band(senal, fs, center_freq, order)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        ruta.unlink(missing_ok=True)
    return wav_response(filtrada, fs, "filtered.wav")
