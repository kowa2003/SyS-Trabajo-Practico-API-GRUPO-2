"""Servicio de filtrado por bandas de octava.

Milestone 2: Procesamiento de la respuesta al impulso.
"""

import numpy as np
from scipy import signal as sps


def filter_single_band(
    signal: np.ndarray, fs: int, center_freq: float, order: int = 4
) -> np.ndarray:
    """Aplica un filtro pasabanda de una octava centrado en ``center_freq`` (IEC 61260).

    Filtro Butterworth pasabanda (``scipy.signal.butter`` con ``output='sos'``)
    con frecuencias de corte:

    - inferior: ``center_freq / sqrt(2)``
    - superior: ``center_freq * sqrt(2)``

    Aplicarlo con ``scipy.signal.sosfiltfilt`` (fase cero), importante para no
    distorsionar EDT y T60. La forma ``(b, a)`` con ``filtfilt`` es inestable en
    las bandas graves.

    Parameters
    ----------
    signal : np.ndarray
        Senal de entrada (array 1D).
    fs : int
        Frecuencia de muestreo en Hz.
    center_freq : float
        Frecuencia central de la banda de octava en Hz.
    order : int, optional
        Orden del filtro Butterworth (por defecto 4).

    Returns
    -------
    np.ndarray
        Senal filtrada (array 1D, misma longitud que ``signal``).
    """

    f_low = center_freq / np.sqrt(2)
    f_high = center_freq * np.sqrt(2)

    if f_high >= fs / 2:
        raise ValueError(
            f"La banda de {center_freq} Hz supera la frecuencia de Nyquist ({fs / 2} Hz)."
        )

    sos = sps.butter(order, [f_low, f_high], btype="bandpass", fs=fs, output="sos")
    return sps.sosfiltfilt(sos, signal)
