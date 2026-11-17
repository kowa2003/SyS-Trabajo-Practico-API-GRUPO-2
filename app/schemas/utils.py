"""Schemas para los endpoints de utilidades acústicas."""

from enum import StrEnum

from pydantic import BaseModel


class SmoothingMethod(StrEnum):
    """Métodos disponibles para calcular la envolvente."""

    HILBERT = "hilbert"
    MOVING_AVERAGE = "moving_average"


class SmoothingResponse(BaseModel):
    """Respuesta del endpoint de suavizado."""

    method: SmoothingMethod
    window_ms: float
    sample_rate: int
    time_step: float
    envelope: list[float]
