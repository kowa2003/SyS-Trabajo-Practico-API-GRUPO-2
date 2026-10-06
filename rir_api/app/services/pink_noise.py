"""Servicio de generacion de ruido rosa.

Milestone 1: Generacion de senales.
"""

import numpy as np


def generate_pink_noise(duration: float, fs: int) -> np.ndarray:
    """Genera una senal de ruido rosa de la duracion especificada.

    El ruido rosa tiene una densidad espectral de potencia inversamente
    proporcional a la frecuencia (1/f): cae -3 dB/octava, de modo que cada
    octava contiene la misma energia. Por eso es util para mediciones acusticas.

    Algoritmo recomendado: **Voss-McCartney**.

    1. Definir ``N_bits`` generadores de ruido blanco (tipicamente 16-20).
    2. Para cada muestra ``n``, actualizar el generador ``i`` cuando el bit ``i``
       de ``n`` cambia respecto de ``n - 1`` (el generador ``i`` se actualiza
       cada ``2**i`` muestras).
    3. Sumar las salidas de todos los generadores.
    4. Normalizar la senal resultante al rango [-1, 1].

    Alternativa aceptable: generar ruido blanco y filtrarlo en frecuencia con
    ``H(f) = 1/sqrt(f)`` (``np.fft.rfft`` -> dividir por ``sqrt(f)`` omitiendo
    ``f = 0`` -> ``np.fft.irfft`` -> normalizar).

    Parameters
    ----------
    duration : float
        Duracion de la senal en segundos.
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    np.ndarray
        Senal de ruido rosa normalizada entre -1 y 1, de longitud
        ``int(duration * fs)``.

    References
    ----------
    .. [1] Voss, R. F. & Clarke, J. (1978). "1/f noise" in music: Music from
       1/f noise. JASA 63(1), 258-263.
    .. [2] https://www.firstpr.com.au/dsp/pink-noise/
    """
    # 1. Calcular cantidad total de muestras
    num_samples = int(duration * fs)

    # 2. Definir cantidad de generadores (N_bits)
    num_rows = 16

    # 3. Crear matriz para los generadores de ruido
    array = np.empty((num_rows, num_samples))

    # El primer generador se actualiza en cada muestra (ruido blanco puro)
    array[0, :] = np.random.randn(num_samples)

    # 4. Actualizar los demás generadores cada 2^i muestras
    for i in range(1, num_rows):
        step = 2**i
        # Generamos valores aleatorios solo para los momentos de cambio
        random_values = np.random.randn(num_samples // step + 2)
        # Repetimos esos valores para mantenerlos constantes y recortamos al tamaño exacto
        array[i, :] = np.repeat(random_values, step)[:num_samples]

    # 5. Sumar las salidas de todos los generadores (colapsar las filas)
    pink_noise = np.sum(array, axis=0)

    # 6. Normalizar la señal resultante al rango [-1, 1]
    pink_noise = pink_noise / np.max(np.abs(pink_noise))

    return pink_noise
