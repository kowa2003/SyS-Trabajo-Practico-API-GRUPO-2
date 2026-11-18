"""Servicio de calculo de parametros acusticos segun ISO 3382.

Milestone 3: Producto final.
"""

import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import hilbert

from app.services.filter import filter_single_band


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
    """Calcula la regresion lineal por minimos cuadrados."""

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if x.ndim != 1 or y.ndim != 1:
        raise ValueError("x e y deben ser arrays unidimensionales")

    if len(x) != len(y):
        raise ValueError("x e y deben tener la misma longitud")

    if len(x) < 2:
        raise ValueError("Se necesitan al menos dos puntos")

    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("x e y deben contener valores finitos")

    x_mean = np.mean(x)
    y_mean = np.mean(y)

    x_centered = x - x_mean
    y_centered = y - y_mean

    denominator = np.sum(x_centered**2)

    if denominator == 0:
        raise ValueError("x es constante")

    slope = np.sum(x_centered * y_centered) / denominator
    intercept = y_mean - slope * x_mean

    y_predicted = slope * x + intercept

    ss_res = np.sum((y - y_predicted) ** 2)
    ss_tot = np.sum((y - y_mean) ** 2)

    r2 = (1.0 if np.isclose(ss_res, 0.0) else 0.0) if ss_tot == 0 else 1.0 - ss_res / ss_tot

    return float(slope), float(intercept), float(r2)


def _estimate_dynamic_range_db(signal: np.ndarray) -> float:
    """Estima el rango dinamico de una senal en dB.

    Compara la potencia pico con la potencia media del ultimo 10%
    de la senal, utilizada como estimacion del ruido de fondo.
    """
    signal = np.asarray(signal, dtype=float)

    if signal.size == 0:
        return 0.0

    power = signal**2

    peak_power = float(np.max(power))

    if peak_power <= 0:
        return 0.0

    # Tomar el ultimo 10% de la senal.
    tail_length = max(1, int(np.ceil(len(signal) * 0.10)))

    noise_power = float(np.mean(power[-tail_length:]))

    if noise_power <= np.finfo(float).tiny:
        return float("inf")

    dynamic_range = 10.0 * np.log10(peak_power / noise_power)

    return float(dynamic_range)


def _calculate_reverberation_time(
    edc_db: np.ndarray,
    fs: int,
    peak_index: int,
    upper_db: float,
    lower_db: float,
    dynamic_range_db: float,
) -> float | None:
    """Calcula un tiempo de reverberacion mediante regresion lineal.

    Utiliza el tramo correspondiente de la curva de Schroeder
    y extrapola la pendiente hasta una caida de 60 dB.

    Devuelve None cuando el rango dinamico es insuficiente
    o la regresion no es confiable.
    """

    # Rango dinámico necesario:
    # tramo de medición + 10 dB por debajo.
    required_range = abs(lower_db) + 10.0

    if dynamic_range_db < required_range:
        return None

    # Crear los índices temporales.
    indices = np.arange(len(edc_db))

    # Seleccionar el intervalo de decaimiento.
    mask = (
        (indices >= peak_index) & (edc_db <= upper_db) & (edc_db >= lower_db) & np.isfinite(edc_db)
    )

    selected_indices = indices[mask]

    if len(selected_indices) < 2:
        return None

    # Convertir las muestras a tiempo en segundos.
    time = (selected_indices - peak_index) / fs

    # Obtener los niveles de la curva de Schroeder.
    levels = edc_db[mask]

    try:
        slope, intercept, r2 = linear_regression(time, levels)
    except ValueError:
        return None

    # La pendiente debe ser negativa.
    if not np.isfinite(slope) or slope >= 0:
        return None

    if not np.isfinite(r2):
        return None

    # Rechazar ajustes que no representan un tramo suficientemente lineal.
    if r2 < 0.99:
        return None

    # Extrapolar el tiempo hasta -60 dB.
    reverberation_time = -60.0 / slope

    if not np.isfinite(reverberation_time):
        return None

    return float(reverberation_time)


def _calculate_energy_parameters(
    band: np.ndarray,
    fs: int,
    peak_index: int,
) -> tuple[float | None, float | None]:
    """Calcula D50 y C80 mediante relaciones de energia."""

    # Considerar la senal desde la llegada directa.
    signal_after_direct = band[peak_index:]

    total_energy = float(np.sum(signal_after_direct**2))

    if total_energy <= 0 or not np.isfinite(total_energy):
        return None, None

    # Cantidad de muestras correspondientes a 50 y 80 ms.
    n50 = int(np.floor(0.050 * fs))
    n80 = int(np.floor(0.080 * fs))

    # --------------------------------
    # D50: energia en los primeros 50 ms
    # --------------------------------

    end_50 = min(peak_index + n50, len(band))

    energy_50 = float(np.sum(band[peak_index:end_50] ** 2))

    d50 = 100.0 * energy_50 / total_energy

    # Limitar el resultado al intervalo porcentual.
    d50 = float(np.clip(d50, 0.0, 100.0))

    # --------------------------------
    # C80: energia temprana / energia tardia
    # --------------------------------

    start_late_80 = min(peak_index + n80, len(band))

    energy_early_80 = float(np.sum(band[peak_index:start_late_80] ** 2))

    energy_late_80 = float(np.sum(band[start_late_80:] ** 2))

    if energy_early_80 <= 0 or energy_late_80 <= 0:
        c80 = None
    else:
        c80 = float(10.0 * np.log10(energy_early_80 / energy_late_80))

    return d50, c80


def calculate_parameters_from_ir(ir: np.ndarray, fs: int) -> dict[str, dict[float, float | None]]:
    """Calcula los parametros acusticos ISO 3382 por banda de octava.

    Calcula EDT, T10, T20, T30, D50 y C80.

    Parameters
    ----------
    ir : np.ndarray
        Respuesta al impulso (array 1D).
    fs : int
        Frecuencia de muestreo en Hz.

    Returns
    -------
    dict[str, dict[float, float | None]]
        Diccionario con los parametros agrupados por frecuencia central.
        Los tiempos que no pueden calcularse devuelven None.
    """

    ir = np.asarray(ir, dtype=float)

    # Validar la respuesta al impulso.
    if ir.ndim != 1 or len(ir) == 0:
        raise ValueError("La RI debe ser un array 1D no vacio")

    if fs <= 0:
        raise ValueError("La frecuencia de muestreo debe ser positiva")

    if not np.all(np.isfinite(ir)):
        raise ValueError("La RI contiene valores no finitos")

    # Bandas de octava que se deben analizar.
    center_frequencies = (
        125.0,
        250.0,
        500.0,
        1000.0,
        2000.0,
        4000.0,
    )

    # Intervalos de decaimiento para cada parametro.
    decay_ranges = {
        "EDT": (0.0, -10.0),
        "T10": (-5.0, -15.0),
        "T20": (-5.0, -25.0),
        "T30": (-5.0, -35.0),
    }

    # Inicializar el diccionario de resultados.
    parameters: dict[str, dict[float, float | None]] = {
        "EDT": {},
        "T10": {},
        "T20": {},
        "T30": {},
        "D50": {},
        "C80": {},
    }

    nyquist = fs / 2.0

    # Recorrer las bandas de octava.
    for center_freq in center_frequencies:
        # Calcular el limite superior de la banda.
        upper_freq = center_freq * np.sqrt(2.0)

        # No analizar bandas que excedan Nyquist.
        if upper_freq >= nyquist:
            continue

        # -----------------------------------------
        # 1. Filtrar la respuesta al impulso
        # -----------------------------------------

        band = filter_single_band(
            ir,
            fs,
            center_freq,
        )

        band = np.asarray(band, dtype=float)

        if band.ndim != 1 or len(band) != len(ir):
            raise ValueError(
                f"El filtro de la banda {center_freq} Hz devolvio una senal de longitud invalida"
            )

        if not np.all(np.isfinite(band)):
            raise ValueError(f"La banda {center_freq} Hz contiene valores no finitos")

        # -----------------------------------------
        # 2. Encontrar la llegada directa
        # -----------------------------------------

        peak_index = int(np.argmax(np.abs(band)))

        # -----------------------------------------
        # 3. Calcular la curva de Schroeder
        # -----------------------------------------

        edc_db = apply_schroeder_integral(band)

        edc_db = np.asarray(edc_db, dtype=float)

        if edc_db.ndim != 1 or len(edc_db) != len(band):
            raise ValueError("La integral de Schroeder devolvio una curva invalida")

        if not np.all(np.isfinite(edc_db)):
            raise ValueError("La curva de Schroeder contiene valores no finitos")

        # -----------------------------------------
        # 4. Estimar el rango dinamico
        # -----------------------------------------

        dynamic_range_db = _estimate_dynamic_range_db(band)

        # -----------------------------------------
        # 5. Calcular EDT, T10, T20 y T30
        # -----------------------------------------

        for parameter_name, (upper_db, lower_db) in decay_ranges.items():
            reverberation_time = _calculate_reverberation_time(
                edc_db=edc_db,
                fs=fs,
                peak_index=peak_index,
                upper_db=upper_db,
                lower_db=lower_db,
                dynamic_range_db=dynamic_range_db,
            )

            parameters[parameter_name][center_freq] = reverberation_time

        # -----------------------------------------
        # 6. Calcular D50 y C80
        # -----------------------------------------

        d50, c80 = _calculate_energy_parameters(
            band=band,
            fs=fs,
            peak_index=peak_index,
        )

        parameters["D50"][center_freq] = d50
        parameters["C80"][center_freq] = c80

    return parameters


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
