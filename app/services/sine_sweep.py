"""Servicio de generacion de sine sweep logaritmico.

Milestone 1: Generacion de senales.
"""

import numpy as np


def generate_sine_sweep_pair(
    duration: float, f1: float, f2: float, fs: int
) -> tuple[np.ndarray, np.ndarray]:
    """Genera un barrido senoidal logaritmico (sine sweep) y su filtro inverso.

    El sweep es ``x(t) = sin[2*pi*f1*T / ln(f2/f1) * (exp(t*ln(f2/f1)/T) - 1)]``
    y el filtro inverso es el sweep invertido en el tiempo con correccion de
    amplitud ``A(t) = exp(-t*ln(f2/f1)/T)`` (tecnica de Farina, 2000). La
    convolucion ``sweep * inverse_filter`` debe aproximar un impulso.

    Parameters
    ----------
    duration : float
        Duracion del barrido en segundos.
    f1 : float
        Frecuencia inicial del barrido en Hz (tipicamente 20 Hz).
    f2 : float
        Frecuencia final del barrido en Hz (tipicamente 20000 Hz).
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    sweep : np.ndarray
        Senal del barrido senoidal, normalizada, de longitud ``int(duration * fs)``.
    inverse_filter : np.ndarray
        Filtro inverso correspondiente, normalizado, de la misma longitud.

    References
    ----------
    .. [1] Farina, A. (2000). "Simultaneous measurement of impulse response
       and distortion with a swept-sine technique." 108th AES Convention.
    """
    # 1. Crear el vector de tiempo discreto
    total_samples = int(duration * fs)
    t = np.linspace(0, duration, total_samples, endpoint=False)

    # Constantes de la formula
    duracion = duration
    razon_log = np.log(f2 / f1)

    # 2. Generar el sine sweep
    # Formula: x(t) = sin[2*pi*f1*T / ln(f2/f1) * (exp(t*ln(f2/f1)/T) - 1)]
    fase = (2 * np.pi * f1 * duracion / razon_log) * (np.exp(t * razon_log / duracion) - 1)
    sweep = np.sin(fase)

    # 3. Generar el filtro inverso (tecnica de Farina)
    sweep_invertido = sweep[::-1]
    # Correccion de amplitud: A(t) = exp(-t*ln(f2/f1)/T)
    amplitud = np.exp(-t * razon_log / duracion)
    inverse_filter = sweep_invertido * amplitud

    # 4. Normalizacion al rango [-1, 1]
    sweep = sweep / np.max(np.abs(sweep))
    inverse_filter = inverse_filter / np.max(np.abs(inverse_filter))
    return sweep, inverse_filter
