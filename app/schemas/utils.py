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


class SchroederResponse(BaseModel):
    sample_rate: int  # la del archivo
    num_samples: int  # largo de la RI original
    lundeby_applied: bool = False  # True si truncaron con apply_lundeby
    time_step: float  # segundos entre dos valores de edc_db
    edc_db: list[float]  # la curva en dB, decimada y sin -inf
