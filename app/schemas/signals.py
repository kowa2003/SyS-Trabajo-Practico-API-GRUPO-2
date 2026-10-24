from pydantic import BaseModel, Field


class PinkNoiseRequest(BaseModel):
    duration: float = Field(gt=0, le=60)
    sample_rate: int = Field(default=44100, ge=8000, le=192000)


class SineSweepRequest(BaseModel):
    duration: float = Field(gt=0, le=60)
    start_freq: float = Field(default=20, gt=1, le=20000)
    end_freq: float = Field(default=20000, gt=1, le=20000)
    sample_rate: int = Field(default=44100, ge=8000, le=192000)
    inverse: bool = Field(default=False)
