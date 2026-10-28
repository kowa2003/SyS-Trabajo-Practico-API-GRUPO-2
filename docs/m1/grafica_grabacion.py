from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf

# Ubicación de los archivos
CARPETA = Path("docs/m1")

# Leer la grabación
grabacion, fs = sf.read(CARPETA / "grabacion_real_m1.wav")

# Si es estéreo, representar el primer canal
if grabacion.ndim == 2:
    grabacion = grabacion[:, 0]

# Vector temporal
tiempo = np.arange(len(grabacion)) / fs

# Graficar la señal
plt.figure(figsize=(11, 4))
plt.plot(tiempo, grabacion, linewidth=0.6)

plt.title("M1 - Grabación real del sine sweep")
plt.xlabel("Tiempo (s)")
plt.ylabel("Amplitud")
plt.grid(True)
plt.tight_layout()

# Guardar gráfica en docs/m1
ruta = CARPETA / "grabacion_real.png"
plt.savefig(ruta, dpi=150)

print("Gráfica guardada en:", ruta)

plt.show()
