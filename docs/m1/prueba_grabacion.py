import sounddevice as sd

print("INICIANDO PRUEBA DE AUDIO")

print("Dispositivos disponibles:")
print(sd.query_devices())

print("Dispositivos predeterminados:")
print(sd.default.device)

from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

from app.services.audio_io import play_and_record
from app.services.sine_sweep import generate_sine_sweep_pair

# Carpeta donde se guardará la grabación
CARPETA = Path("docs/m1")
CARPETA.mkdir(parents=True, exist_ok=True)

# Configuración de la prueba
fs = 44100
duracion_sweep = 3.0
duracion_grabacion = 5.0

# Consultar dispositivos disponibles
print("Dispositivos de audio disponibles:")
print(sd.query_devices())
print("Dispositivos predeterminados:", sd.default.device)
print("Buffer:", sd.default.blocksize)

# Generar el sine sweep
sweep, inverso = generate_sine_sweep_pair(
    duration=duracion_sweep,
    f1=100,
    f2=5000,
    fs=fs,
)

# Agregar 0.5 segundos de silencio inicial
silencio = np.zeros(int(0.5 * fs))
senal = np.concatenate([silencio, sweep])

# Reducir amplitud para evitar saturación
senal = 0.2 * senal

# Reproducir y grabar simultáneamente
print("Iniciando reproducción y grabación...")

grabacion = play_and_record(
    signal=senal,
    fs=fs,
    record_duration=duracion_grabacion,
)

# Guardar archivo WAV
ruta = CARPETA / "grabacion_real_m1.wav"
sf.write(ruta, grabacion, fs)

print("Grabación completada.")
print("Forma:", grabacion.shape)
print("Amplitud máxima:", np.max(np.abs(grabacion)))
print("Archivo guardado en:", ruta)
