"""Schemas Pydantic para la validación de peticiones de generación de señales.

Define los modelos de datos de entrada utilizados por los endpoints del router
de señales (``/api/v1/signals/*``) para validar parámetros temporales,
espectrales y de muestreo antes de ejecutar los servicios de procesamiento.
"""

from pydantic import BaseModel, Field, PositiveFloat


class PinkNoiseRequest(BaseModel):
    duration: float = Field(gt=0, le=60)
    sample_rate: int = Field(default=44100, ge=8000, le=192000)


class SineSweepRequest(BaseModel):
    duration: float = Field(gt=0, le=60)
    start_freq: float = Field(default=20, ge=1, le=20000)
    end_freq: float = Field(default=20000, ge=1, le=20000)
    sample_rate: int = Field(default=44100, ge=8000, le=192000)
    inverse: bool = Field(default=False)


class SyntheticIRRequest(BaseModel):
    duration: float = Field(gt=0, le=10)
    t60_values: dict[PositiveFloat, PositiveFloat] = Field(min_length=1)
    sample_rate: int = Field(default=44100, ge=8000, le=192000)
