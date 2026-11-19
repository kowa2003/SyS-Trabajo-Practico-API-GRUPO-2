"""Endpoints de utilidades acústicas."""

from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.routers.audio_http import uploaded_file
from app.schemas.utils import SchroederResponse, SmoothingMethod, SmoothingResponse
from app.services.acoustic_parameters import apply_schroeder_integral, apply_smoothing
from app.services.signal_utils import load_audio

router = APIRouter()


@router.post("/smoothing", response_model=SmoothingResponse)
async def smoothing(
    file: Annotated[UploadFile, File()],
    method: Annotated[SmoothingMethod, Form()] = SmoothingMethod.HILBERT,
    window_ms: Annotated[float, Form(gt=0, le=100)] = 10.0,
) -> SmoothingResponse:
    """Recibe un audio y devuelve su envolvente de amplitud."""

    try:
        # Cargar el archivo subido mediante el servicio de M2.
        with uploaded_file(file) as path:
            signal, fs = load_audio(path)

        # Calcular la envolvente.
        envelope = apply_smoothing(
            signal,
            fs,
            method=method.value,
            window_ms=window_ms,
        )

    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    # Reducir los datos enviados a aproximadamente 1000 puntos/s.
    paso = max(1, round(fs / 1000))
    envelope_reducida = envelope[::paso]

    return SmoothingResponse(
        method=method,
        window_ms=window_ms,
        sample_rate=fs,
        time_step=paso / fs,
        envelope=envelope_reducida.tolist(),
    )


@router.post("/schroeder", response_model=SchroederResponse)
async def schroeder(
    file: Annotated[UploadFile, File(...)],
) -> SchroederResponse:
    with uploaded_file(file) as path:
        try:
            signal, fs = load_audio(path)
        except Exception as exc:
            raise HTTPException(
                status_code=422, detail=f"Archivo de audio inválido: {exc}"
            ) from exc

    num_samples = len(signal)
    edc = apply_schroeder_integral(signal)

    paso = max(1, round(fs / 1000))
    decimated_edc = edc[::paso].tolist()
    time_step = paso / fs

    return SchroederResponse(
        sample_rate=fs,
        num_samples=num_samples,
        lundeby_applied=False,
        time_step=time_step,
        edc_db=decimated_edc,
    )
