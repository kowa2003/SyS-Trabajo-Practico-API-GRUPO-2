from fastapi import APIRouter

from app.routers.audio_http import wav_response
from app.schemas.signals import PinkNoiseRequest, SineSweepRequest
from app.services.pink_noise import generate_pink_noise
from app.services.sine_sweep import generate_sine_sweep_pair

router = APIRouter()


@router.post("/pink-noise")
async def pink_noise(req: PinkNoiseRequest):
    audio = generate_pink_noise(req.duration, req.sample_rate)
    return wav_response(audio, req.sample_rate, "pink_noise.wav")


@router.post("/sine-sweep")
async def sine_sweep(req: SineSweepRequest):
    if req.f1 >= req.f2:
        raise ValueError("f1 tiene que ser menor que f2")
    sweep, inverse_filter = generate_sine_sweep_pair(req.duration, req.f1, req.f2, req.sample_rate)
    return (
        wav_response(sweep, req.sample_rate, "sine_sweep.wav")
        if not req.inverse
        else wav_response(inverse_filter, req.sample_rate, "inverse_filter.wav")
    )
