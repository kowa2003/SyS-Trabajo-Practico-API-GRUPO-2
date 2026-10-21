from pydantic import BaseModel, Field


class PinkNoiseRequest(BaseModel):
    duration: float = Field(gt=0, le=60)
    sample_rate: int = Field(default=44100, ge=8000, le=192000)
