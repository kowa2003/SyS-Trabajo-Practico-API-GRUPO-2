"""Servicio de calculo de parametros acusticos segun ISO 3382.

Milestone 3: Producto final.
"""

import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import hilbert


def apply_smoothing(
    signal: np.ndarray, fs: int, method: str = "hilbert", window_ms: float = 10
) -> np.ndarray:
    """Suaviza una senal y devuelve su envolvente en **amplitud**.

    - ``method='hilbert'`` (recomendado): envolvente de Hilbert,
      ``np.abs(scipy.signal.hilbert(signal))``. Ignora ``window_ms``.
    - ``method='moving_average'``: media movil de ``window_ms`` milisegundos
      (``int(window_ms * fs / 1000)`` muestras, al menos 1). Para que la salida
      quede en amplitud (comparable con Hilbert), devolver la raiz de la media
      movil de ``signal**2`` (envolvente RMS) o, alternativamente, la media
      movil de ``|signal|``. Documentar cual se eligio.

    Parameters
    ----------
    signal : np.ndarray
        Senal de entrada (tipicamente una RI filtrada por banda, array 1D).
    fs : int
        Frecuencia de muestreo en Hz (para convertir ``window_ms`` a muestras).
    method : str, optional
        ``'hilbert'`` (por defecto) o ``'moving_average'``.
    window_ms : float, optional
        Largo de la ventana de media movil en milisegundos (por defecto 10 ms).

    Returns
    -------
    np.ndarray
        Envolvente en amplitud (no negativa), de la misma longitud que ``signal``.

    Raises
    ------
    ValueError
        Si ``method`` no es ``'hilbert'`` ni ``'moving_average'``, o si
        ``window_ms`` no es positivo.
    """

    # Convertir la señal a un arreglo NumPy de precisión doble.
    x = np.asarray(signal, dtype=np.float64)

    # Validar las entradas.
    if x.ndim != 1 or x.size == 0 or not np.all(np.isfinite(x)):
        raise ValueError("La señal debe ser un array 1D no vacío y con valores finitos.")

    if fs <= 0:
        raise ValueError("La frecuencia de muestreo debe ser positiva.")

    if not np.isfinite(window_ms) or window_ms <= 0:
        raise ValueError("window_ms debe ser positivo y finito.")

    # Método 1: envolvente mediante la transformada de Hilbert.
    if method == "hilbert":
        return np.abs(hilbert(x))

    # Método 2: media móvil RMS.
    if method == "moving_average":
        window = max(1, int(window_ms * fs / 1000))

        # Promediar la potencia instantánea dentro de la ventana.
        potencia_local = uniform_filter1d(x**2, size=window, mode="reflect")

        # Volver a unidades de amplitud.
        return np.sqrt(np.maximum(potencia_local, 0.0))

    raise ValueError("method debe ser 'hilbert' o 'moving_average'.")


def apply_schroeder_integral(ir: np.ndarray) -> np.ndarray:
    """Calcula la integral de Schroeder (Energy Decay Curve) en dB.

    ``E[n] = sum_{k=n}^{N-1} h[k]**2`` (integracion inversa, por ejemplo con
    ``np.cumsum`` sobre la senal invertida) y ``L[n] = 10*log10(E[n] / E[0])``.

    Parameters
    ----------
    ir : np.ndarray
        Respuesta al impulso (o RI filtrada por banda, array 1D).

    Returns
    -------
    np.ndarray
        Curva de decaimiento en dB, normalizada a 0 dB en la primera muestra,
        de la misma longitud que ``ir``.

    References
    ----------
    .. [1] Schroeder, M. R. (1965). "New method of measuring reverberation
       time." JASA 37(3), 409-412.
    """
    # 1. Energía instantánea al cuadrado (h^2)
    ir_sq = ir**2

    # 2. Integración inversa: acumular de atrás hacia adelante
    e_t = np.cumsum(ir_sq[::-1])[::-1]

    # 3. Obtener la energía total inicial (E[0]) como float
    e_0 = float(e_t[0])

    # 4. Manejo de seguridad si la señal no tiene energía o es inválida
    if not np.isfinite(e_0) or e_0 <= 0:
        return np.full_like(ir, -150.0, dtype=float)

    # 5. Normalizar PRIMERO para obtener el ratio adimensional (entre 0 y 1)
    ratio = e_t / e_0

    # 6. Limitar el ratio usando np.clip con la fórmula exacta de -150 dB (10^(-150/10))
    # Esto evita valores positivos y fija un piso seguro sin depender de amplitudes absolutas.
    ratio = np.clip(ratio, 10.0 ** (-150.0 / 10.0), 1.0)

    # 7. Conversión final a decibelios energéticos (10 * log10)
    edc_db = 10.0 * np.log10(ratio)

    return edc_db


def linear_regression(x: np.ndarray, y: np.ndarray) -> tuple[float, float, float]:
    """Calcula la regresion lineal por minimos cuadrados.

    Se recomienda implementarla a mano (formulas de minimos cuadrados) en lugar
    de ``np.polyfit``, para demostrar comprension del metodo.

    Parameters
    ----------
    x : np.ndarray
        Variable independiente (tipicamente tiempo en segundos).
    y : np.ndarray
        Variable dependiente (tipicamente curva de Schroeder en dB).

    Returns
    -------
    slope : float
        Pendiente de la recta ajustada ``m`` (dB/s en el contexto acustico).
    intercept : float
        Ordenada al origen ``b`` (dB).
    r2 : float
        Coeficiente de determinacion R^2.
    """
    raise NotImplementedError("Implementar en Milestone 3")


def calculate_parameters_from_ir(ir: np.ndarray, fs: int) -> dict[str, dict[float, float]]:
    """Calcula los parametros acusticos ISO 3382 por banda de octava.

    Parametros: EDT (0 a -10 dB), T10 (-5 a -15 dB), T20 (-5 a -25 dB),
    T30 (-5 a -35 dB), D50 (%) y C80 (dB).

    Parameters
    ----------
    ir : np.ndarray
        Respuesta al impulso (array 1D).
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    dict[str, dict[float, float]]
        ``{parametro: {frecuencia_central: valor}}``.
        Ejemplo: ``{'T30': {125: 1.5, 250: 1.3, ...}, 'EDT': {...}, 'D50': {...},
        'C80': {...}}``.

    References
    ----------
    .. [1] ISO 3382-1:2009. "Acoustics -- Measurement of room acoustic
       parameters -- Part 1: Performance spaces."
    """
    raise NotImplementedError("Implementar en Milestone 3")


def apply_lundeby(ir: np.ndarray, fs: int) -> tuple[int, float]:
    """Estima el punto de truncamiento de la RI (metodo de Lundeby).

    Parameters
    ----------
    ir : np.ndarray
        Respuesta al impulso (array 1D).
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    index : int
        Indice de la muestra donde la RI se cruza con el ruido de fondo.
    noise_level_db : float
        Nivel estimado del ruido de fondo en dB.

    Notes
    -----
    Esta funcion es **opcional** (extra).

    References
    ----------
    .. [1] Lundeby, A. et al. (1995). "Uncertainties of measurements in
       room acoustics." Acustica 81(4), 344-355.
    """
    raise NotImplementedError("Implementar en Milestone 3 (opcional)")
