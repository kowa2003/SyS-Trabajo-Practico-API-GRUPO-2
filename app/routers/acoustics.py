"""Router para el analisis de parametros acusticos."""

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.routers.audio_http import uploaded_file
from app.schemas.responses import BandAnalysisResponse
from app.services.acoustic_parameters import calculate_parameters_from_ir
from app.services.signal_utils import load_audio

router = APIRouter()


@router.post(
    "/parameters",
    response_model=BandAnalysisResponse,
)
async def parameters(
    file: Annotated[UploadFile, File(...)],
) -> BandAnalysisResponse:
    """Recibe una RI WAV y devuelve los parametros acusticos ISO 3382."""

    # Cargar el archivo WAV.
    try:
        with uploaded_file(file) as path:
            ir, fs = load_audio(path)

    except Exception as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Archivo de audio invalido: {exc}",
        ) from exc

    # Calcular los parametros acusticos.
    try:
        params = calculate_parameters_from_ir(ir, fs)

    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Error al analizar la respuesta al impulso: {exc}",
        ) from exc

    # Obtener las frecuencias analizadas.
    center_frequencies = sorted(params["EDT"].keys())

    # Construir la respuesta.
    return BandAnalysisResponse(
        sample_rate=fs,
        duration=len(ir) / fs,
        center_frequencies=center_frequencies,
        parameters=params,
    )
