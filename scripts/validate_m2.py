import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# 1. Asegurar importación de servicios del proyecto
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.services.filter import filter_single_band
from app.services.signal_utils import load_audio, logarithmic_scale_conversion

# 2. Definir rutas y configuración
m2_dir = Path("docs/m2")

# Archivos WAV a procesar
files_to_process = [
    "h042_Hallway_ElementarySchool_4txts.wav",
    "h045_Livingroom_4txts.wav",
]

# Bandas de octava normalizadas (ISO/IEC 61260)
center_frequencies = [125, 250, 500, 1000, 2000, 4000]

for file_name in files_to_process:
    audio_path = m2_dir / file_name

    if not audio_path.exists():
        print(f"⚠️ Archivo no encontrado: {audio_path}. Omitiendo...")
        continue

    print(f"\nProcesando {audio_path.name} en 6 bandas de octava...")

    # Cargar y normalizar audio
    signal, fs = load_audio(audio_path)
    time = np.arange(len(signal)) / fs

    # ---------------------------------------------------------
    # 1. Forma de onda de la respuesta impulsional original
    # ---------------------------------------------------------
    plt.figure(figsize=(12, 4))
    plt.plot(time, signal, linewidth=0.7)

    plt.title(f"Forma de onda - {audio_path.stem}")
    plt.xlabel("Tiempo [s]")
    plt.ylabel("Amplitud")
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()

    output_waveform = m2_dir / f"forma_onda_{audio_path.stem}.png"
    plt.savefig(output_waveform, dpi=300)
    plt.close()

    print(f"Forma de onda guardada en: {output_waveform}")

    # ---------------------------------------------------------
    # 2. Espectro de magnitud de la respuesta impulsional
    # ---------------------------------------------------------
    N = len(signal)

    # Ventana Hann para reducir la fuga espectral
    window = np.hanning(N)
    windowed_signal = signal * window

    # Transformada de Fourier para señales reales
    spectrum = np.abs(np.fft.rfft(windowed_signal))

    # Escala de amplitud de un solo lado
    spectrum = spectrum / np.sum(window)
    spectrum[1:-1] *= 2

    frequencies = np.fft.rfftfreq(N, d=1 / fs)

    # Expresar el espectro en dB, referido a su máximo
    spectrum_db = 20 * np.log10(np.maximum(spectrum / np.max(spectrum), 1e-6))

    # Diagnóstico del contenido espectral
    for freq in [8000, 10000, 12000, 14000, 16000]:
        idx = np.argmin(np.abs(frequencies - freq))
        print(f"{freq} Hz: {spectrum_db[idx]:.2f} dB")

    plt.figure(figsize=(12, 4))
    plt.plot(frequencies, spectrum_db, linewidth=0.8)

    plt.title(f"Espectro de magnitud - {audio_path.stem}")
    plt.xlabel("Frecuencia [Hz]")
    plt.ylabel("Magnitud relativa [dB]")
    plt.xlim(0, fs / 2)
    plt.ylim(-120, 5)
    plt.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()

    output_spectrum = m2_dir / f"espectro_{audio_path.stem}.png"
    plt.savefig(output_spectrum, dpi=300)
    plt.close()

    print(f"Espectro guardado en: {output_spectrum}")

    # Crear figura de 6 filas (una por cada banda)
    fig, axes = plt.subplots(len(center_frequencies), 1, figsize=(12, 14), sharex=True)
    fig.suptitle(
        f"Validación Acústica Multi-banda (M2): {audio_path.stem}",
        fontsize=14,
        fontweight="bold",
    )

    for i, fc in enumerate(center_frequencies):
        # A. Filtrar en la banda especificada
        filtered = filter_single_band(signal, fs, center_freq=float(fc), order=4)

        # B. Convertir a escala logarítmica (dB)
        log_signal = logarithmic_scale_conversion(filtered)

        # C. Graficar la curva de decaimiento en el panel correspondiente
        ax = axes[i]
        ax.plot(time, log_signal, label=f"{fc} Hz", color=f"C{i}")
        ax.set_ylabel("Nivel [dB]")
        ax.set_ylim([-80, 5])
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(loc="upper right")

    axes[-1].set_xlabel("Tiempo [s]")
    plt.tight_layout()

    # Guardar imagen con el análisis multi-banda
    output_png = m2_dir / f"val_multiband_{audio_path.stem}.png"
    plt.savefig(output_png, dpi=300)
    plt.close()

    floor_count = np.sum(spectrum_db <= -119.99)

    print(f"Muestras en el piso de -120 dB: {floor_count}/{len(spectrum_db)}")

    print(f"✓ Gráfica multi-banda guardada exitosamente en: {output_png}")
