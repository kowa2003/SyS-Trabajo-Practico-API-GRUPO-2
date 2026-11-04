"""Prueba real de M1. Ejecutar desde la raíz: uv run python -m docs.m1.prueba_grabacion."""

from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

from app.services.audio_io import play_and_record
from app.services.sine_sweep import generate_sine_sweep_pair


def main() -> None:
    """Reproduce un sweep mono, graba cinco segundos y guarda los datos de la prueba."""
    carpeta = Path(__file__).resolve().parent
    fs = 44100
    duracion_sweep = 3.0
    duracion_grabacion = 5.0
    canales = 1

    # None utiliza el dispositivo predeterminado. Para elegir otro, poner su
    # número según la lista que imprime el script (entrada y salida por separado).
    dispositivo_entrada = None
    dispositivo_salida = None
    if dispositivo_entrada is not None:
        sd.default.device[0] = dispositivo_entrada
    if dispositivo_salida is not None:
        sd.default.device[1] = dispositivo_salida

    print("DISPOSITIVOS DISPONIBLES")
    print(sd.query_devices())
    entrada = sd.query_devices(kind="input")
    salida = sd.query_devices(kind="output")
    sd.check_input_settings(samplerate=fs, channels=canales, dtype="float32")
    sd.check_output_settings(samplerate=fs, channels=canales, dtype="float32")

    buffer = sd.default.blocksize
    detalle_buffer = "automático, elegido por PortAudio" if buffer == 0 else "muestras"
    configuracion = (
        "Prueba real M1\n"
        f"Entrada: {entrada['name']}\n"
        f"Salida: {salida['name']}\n"
        f"Canales de entrada: {canales}\n"
        f"Canales de salida: {canales}\n"
        f"Frecuencia de muestreo: {fs} Hz\n"
        f"Buffer configurado: {buffer} ({detalle_buffer})\n"
        "Sweep: 100 Hz a 5000 Hz\n"
        f"Duración del sweep: {duracion_sweep} s\n"
        f"Duración de grabación: {duracion_grabacion} s\n"
        "Factor de amplitud: 0.2\n"
        "Silencio inicial: 0.5 s, agregado por play_and_record\n"
        "Silencio posterior: 1.5 s\n"
    )
    print("\nCONFIGURACIÓN")
    print(configuracion)

    sweep, _ = generate_sine_sweep_pair(duracion_sweep, 100, 5000, fs)
    # El servicio ya agrega el silencio inicial: no duplicarlo aquí.
    senal = (0.2 * sweep).astype(np.float32)
    print("Iniciando reproducción y grabación...")
    grabacion = play_and_record(senal, fs, duracion_grabacion)
    if grabacion.size == 0 or not np.isfinite(grabacion).all():
        raise RuntimeError("La grabación está vacía o contiene valores no finitos.")

    ruta = carpeta / "grabacion_real_m1.wav"
    sf.write(ruta, grabacion, fs, subtype="PCM_16")
    resultado = (
        f"Forma: {grabacion.shape}\n"
        f"Duración obtenida: {len(grabacion) / fs:.3f} s\n"
        f"Amplitud máxima: {np.max(np.abs(grabacion)):.6f}\n"
        "Observación de escucha: completar después de escuchar el WAV.\n"
    )
    registro = carpeta / "configuracion_grabacion_m1.txt"
    registro.write_text(configuracion + "\n" + resultado, encoding="utf-8")
    print("Grabación completada.")
    print(resultado)
    print("WAV guardado en:", ruta)
    print("Configuración guardada en:", registro)


if __name__ == "__main__":
    main()
