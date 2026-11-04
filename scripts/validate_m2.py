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

    print(f"✓ Gráfica multi-banda guardada exitosamente en: {output_png}")
