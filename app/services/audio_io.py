"""Servicio de reproduccion y grabacion simultanea.

Milestone 1: Generacion de senales.

``sounddevice`` se importa **dentro** de la funcion (import perezoso): asi el
resto de la API, los tests y el CI funcionan en maquinas sin placa de audio.
"""

import numpy as np


def play_and_record(signal: np.ndarray, fs: int, record_duration: float) -> np.ndarray:
    """Reproduce una senal y graba simultaneamente (``sounddevice.playrec``).

    Parameters
    ----------
    signal : np.ndarray
        Senal a reproducir (1D mono o 2D ``(muestras, canales)``).
    fs : int
        Frecuencia de muestreo en Hz.
    record_duration : float
        Duracion total de la grabacion en segundos.

    Returns
    -------
    np.ndarray
        Senal grabada, con ``int(record_duration * fs)`` muestras.

    Raises
    ------
    ValueError
        Si ``record_duration`` es menor a la duracion de la senal.
    RuntimeError
        Si no hay un dispositivo de audio disponible (con un mensaje informativo).
    """
    target_samples = int(record_duration * fs)
    signal_samples = len(signal)

    # Validar que record_duration sea mayor o igual a la duración de la señal
    if target_samples < signal_samples:
        raise ValueError(
            f"record_duration ({record_duration}s) debe ser mayor o igual "
            f"a la duración de la señal ({signal_samples / fs:.2f}s)."
        )

    # Calcular margen sobrante para pre-roll (latencia) y post-roll (reverberación)
    extra_samples = target_samples - signal_samples
    desired_preroll_samples = int(0.5 * fs)

    pre_roll_samples = min(desired_preroll_samples, extra_samples)
    post_roll_samples = extra_samples - pre_roll_samples

    # Formatear la señal para Mono (1D) o Estéreo/Multicanal (2D)
    if signal.ndim == 1:
        channels = 1
        pre_roll = np.zeros(pre_roll_samples, dtype=signal.dtype)
        post_roll = np.zeros(post_roll_samples, dtype=signal.dtype)
        padded_signal = np.concatenate([pre_roll, signal, post_roll])
    elif signal.ndim == 2:
        channels = signal.shape[1]
        pre_roll = np.zeros((pre_roll_samples, channels), dtype=signal.dtype)
        post_roll = np.zeros((post_roll_samples, channels), dtype=signal.dtype)
        padded_signal = np.vstack([pre_roll, signal, post_roll])
    else:
        raise ValueError("La señal debe ser de dimensión 1D (mono) o 2D (estéreo/multicanal).")

    # Importación perezosa DENTRO del try para permitir que monkeypatch inyecte el mock
    try:
        import sounddevice as sd

        devices = sd.query_devices()
        if not devices:
            raise RuntimeError("No se detectaron dispositivos de audio disponibles en el sistema.")

        recorded = sd.playrec(
            padded_signal,
            samplerate=fs,
            channels=channels,
            dtype="float32",
            blocking=True,
        )
        return recorded

    except Exception as e:
        # Captura PortAudioError u otras excepciones del mock y relanza RuntimeError
        raise RuntimeError(
            f"No hay un dispositivo de audio disponible para grabar/reproducir: {e}"
        ) from e
