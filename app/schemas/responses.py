from pydantic import BaseModel


class BandAnalysisResponse(BaseModel):
    """Respuesta del analisis de parametros acusticos."""

    sample_rate: int
    duration: float
    center_frequencies: list[float]
    parameters: dict[str, dict[float, float | None]]
