"""Utilidades de procesamiento de senales.

Milestone 2: Procesamiento de la respuesta al impulso.
"""
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve


def load_audio(path: str | Path) -> tuple[np.ndarray, int]:
    """Carga un archivo WAV o FLAC y devuelve la señal mono y su frecuencia.

    Devuelve un arreglo 1D de tipo float64. Si el archivo tiene varios
    canales, los promedia para obtener mono. Conserva el nivel del audio,
    sin normalizarlo respecto de su amplitud máxima.

    Parameters
    ----------
    path : str | Path
        Ruta del archivo de audio.

    Returns
    -------
    tuple[np.ndarray, int]
        Señal mono y frecuencia de muestreo en Hz.

    Raises
    ------
    FileNotFoundError
        Si el archivo no existe.
    ValueError
        Si el archivo no puede leerse como audio.
    """
    ruta = Path(path)

    if not ruta.exists():
        raise FileNotFoundError(f"No existe el archivo: {ruta}")

    try:
        signal, fs = sf.read(ruta, dtype="float64")
    except sf.LibsndfileError as error:
        raise ValueError(f"No se pudo leer el archivo de audio '{ruta}': {error}") from error

    # En audio multicanal, cada columna corresponde a un canal.
    if signal.ndim == 2:
        signal = signal.mean(axis=1)

    return signal, fs


def generate_synthetic_ir(duration: float, t60_values: dict[float, float], fs: int) -> np.ndarray:
    """Sintetiza una respuesta al impulso con valores de T60 conocidos por banda.

    Modelo: ``h(t) = n(t) * exp(-alpha * t)`` con ``alpha = 3 * ln(10) / T60``,
    donde ``n(t)`` es ruido blanco filtrado en la banda de octava. Se suman las
    componentes de todas las bandas y se normaliza.

    Parameters
    ----------
    duration : float
        Duracion de la respuesta al impulso en segundos.
    t60_values : dict[float, float]
        Diccionario ``{frecuencia_central_Hz: T60_segundos}``.
        Ejemplo: ``{125: 2.0, 250: 1.8, 500: 1.5, 1000: 1.2, 2000: 1.0, 4000: 0.8}``.
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    np.ndarray
        Respuesta al impulso sintetizada (array 1D de ``int(duration * fs)`` muestras).
    """
    raise NotImplementedError("Implementar en Milestone 2")


def get_impulse_response(recording: np.ndarray, inverse_filter: np.ndarray) -> np.ndarray:
    """Obtiene la respuesta al impulso mediante deconvolucion de un sine sweep.

    ``h(t) = y(t) * x_inv(t)``, con ``y = recording`` y ``x_inv = inverse_filter``;
    usar ``scipy.signal.fftconvolve`` (``mode='full'``), recortar para que la RI
    comience en el pico (o ligeramente antes) y normalizar respecto del pico.

    Parameters
    ----------
    recording : np.ndarray
        Senal grabada que contiene la respuesta de la sala al sweep.
    inverse_filter : np.ndarray
        Filtro inverso del sweep utilizado.

    Returns
    -------
    np.ndarray
        Respuesta al impulso estimada, normalizada.
    """
    # 1. Validar las senales de entrada.
    if recording.ndim != 1 or inverse_filter.ndim != 1:
        raise ValueError("Las senales deben tener una dimension.")

    if recording.size == 0 or inverse_filter.size == 0:
        raise ValueError("Las senales no pueden estar vacias.")

    # 2. Convolucion completa utilizando FFT.
    ir_full = fftconvolve(recording, inverse_filter, mode="full")

    # 3. Encontrar el pico del sonido directo.
    peak_idx = int(np.argmax(np.abs(ir_full)))

    # 4. Conservar 240 muestras antes del pico (~5 ms a 48 kHz).
    pre_samples = 240
    start_idx = max(0, peak_idx - pre_samples)
    ir = ir_full[start_idx:]

    # 5. Normalizar respecto de la amplitud maxima.
    peak_amplitude = np.max(np.abs(ir))

    if not np.isfinite(peak_amplitude) or peak_amplitude == 0:
        raise ValueError("No se puede normalizar una senal sin pico valido.")

    return ir / peak_amplitude


def logarithmic_scale_conversion(signal: np.ndarray) -> np.ndarray:
    """Convierte una senal a escala logaritmica (dB) normalizada.

    ``L = 20 * log10(|x| / max(|x|))``. Evitar ``log(0)`` (usar un ``eps`` o
    un piso, por ejemplo -120 dB).

    Parameters
    ----------
    signal : np.ndarray
        Senal de entrada (valores lineales, array 1D).

    Returns
    -------
    np.ndarray
        Senal en dB, normalizada a 0 dB en el maximo.
    """
    raise NotImplementedError("Implementar en Milestone 2")
