"""Validación M3: RI sintética + Hallway + Livingroom, API real vs REW.

Desde la raíz del repositorio:
    python docs/m3/validar_m3.py

No modifica services ni WAV originales. Genera CSV, JSON, PNG y Markdown
exclusivamente dentro de docs/m3/. Usa el código de la rama activa.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import soundfile as sf  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from scipy import signal as sps  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402
from app.services.acoustic_parameters import (  # noqa: E402
    apply_schroeder_integral,
    apply_smoothing,
)
from app.services.filter import filter_single_band  # noqa: E402
from app.services.signal_utils import generate_synthetic_ir, load_audio  # noqa: E402

DESTINO = ROOT / "docs" / "m3"
M2 = ROOT / "docs" / "m2"
BANDAS = (125, 250, 500, 1000, 2000, 4000)
RI_REALES = {
    "Hallway": ("h042", "h042_Hallway_ElementarySchool_4txts.wav"),
    "Livingroom": ("h045", "h045_Livingroom_4txts.wav"),
}
T60_OBJETIVO = {125: 2.0, 250: 1.8, 500: 1.5, 1000: 1.2, 2000: 1.0, 4000: 0.8}
RANGOS = {"EDT": (0.0, -10.0), "T20": (-5.0, -25.0), "T30": (-5.0, -35.0)}
PARAMS_NORMA = ("EDT", "T20", "T30", "C80")
COLORES = {"EDT": "#E78B4D", "T20": "#18A69A", "T30": "#8D6BCC"}
plt.rcParams.update({"font.size": 10, "axes.titlesize": 12, "figure.dpi": 130})


def valor(params: dict, parametro: str, banda: int) -> float | None:
    """Lee claves numéricas del service y claves string del JSON sin falsear None."""
    registro = params.get(parametro, {})
    for clave in (str(float(banda)), str(banda), float(banda), banda):
        if clave in registro:
            x = registro[clave]
            return None if x is None else float(x)
    raise KeyError(f"Falta {parametro} en {banda} Hz: {list(registro)}")


def estado_git() -> dict:
    def git(*args: str) -> str:
        try:
            return subprocess.check_output(
                ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL
            ).strip()
        except (OSError, subprocess.CalledProcessError):
            return "no disponible"

    return {
        "rama": git("branch", "--show-current"),
        "commit": git("rev-parse", "--short", "HEAD"),
        "cambios_sin_commit": (
            None
            if git("status", "--porcelain") == "no disponible"
            else bool(git("status", "--porcelain"))
        ),
    }


def analizar_wav(cliente: TestClient, archivo: Path) -> dict:
    """Pasa por la ruta POST real de FastAPI; no reimplementa la API."""
    with archivo.open("rb") as audio:
        response = cliente.post(
            "/api/v1/acoustics/parameters",
            files={"file": (archivo.name, audio, "audio/wav")},
        )
    if response.status_code != 200:
        raise RuntimeError(
            f"Endpoint falló con {archivo.name}: {response.status_code}: {response.text[:600]}"
        )
    data = response.json()
    if not all(x in data for x in ("sample_rate", "duration", "parameters")):
        raise RuntimeError(f"Respuesta inesperada para {archivo.name}: {data}")
    for p in ("EDT", "T10", "T20", "T30", "D50", "C80"):
        for b in BANDAS:
            valor(data["parameters"], p, b)
    return data


def generar_sintetica(cliente: TestClient) -> dict:
    fs = 44100
    ir = generate_synthetic_ir(duration=5.0, t60_values=T60_OBJETIVO, fs=fs)
    archivo = DESTINO / "ri_sintetica_m3.wav"
    sf.write(archivo, ir, fs, subtype="FLOAT")
    return analizar_wav(cliente, archivo)


def inicio_directo_diagnostico(ir: np.ndarray, fs: int) -> int:
    """Reconstrucción VISUAL de la heurística experimental de onset del 10%.

    No reemplaza a calculate_parameters_from_ir ni se usa para el CSV/API.
    """
    pico = int(np.argmax(np.abs(ir)))
    inicio_busqueda = max(0, pico - int(0.005 * fs))
    umbral = 0.10 * float(np.abs(ir[pico]))
    candidatos = np.flatnonzero(np.abs(ir[inicio_busqueda : pico + 1]) >= umbral)
    return inicio_busqueda + int(candidatos[0]) if len(candidatos) else pico


def salvar_figura(fig: plt.Figure, nombre: str) -> None:
    fig.savefig(DESTINO / nombre, dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  Gráfico: docs/m3/{nombre}")


def grafica_schroeder(ir: np.ndarray, fs: int, resultado: dict, nombre: str, cod: str) -> None:
    """EDC y rectas reconstruidas con los tiempos devueltos por el endpoint.

    Para visualizar, se usa la referencia temporal experimental. Si en la rama
    cambia la detección de inicio, la curva será diagnóstica, no auditoría interna.
    """
    banda = filter_single_band(ir, fs, 1000.0)
    edc = np.asarray(apply_schroeder_integral(banda), dtype=float)
    n0 = inicio_directo_diagnostico(ir, fs)
    edc = edc - edc[n0]
    tiempos = np.arange(len(ir)) / fs
    fig, ax = plt.subplots(figsize=(11.5, 6.5))
    ax.plot(tiempos, edc, color="#254C72", lw=1.65, label="Schroeder · 1000 Hz")
    ax.axvline(n0 / fs, ls=":", lw=1.5, color="#475569", label="Inicio estimado")
    for parametro, (alto, bajo) in RANGOS.items():
        mask = (np.arange(len(edc)) >= n0) & (edc <= alto) & (edc >= bajo)
        mask &= np.isfinite(edc)
        indices = np.flatnonzero(mask)
        t_api = valor(resultado["parameters"], parametro, 1000)
        if indices.size < 2 or t_api is None or t_api <= 0:
            continue
        # Pendiente tomada del resultado REAL del endpoint, sin recalcular T.
        pendiente = -60.0 / t_api
        t0 = n0 / fs
        intercepto = float(np.mean(edc[mask] - pendiente * (tiempos[mask] - t0)))
        x = np.array([tiempos[indices[0]], tiempos[indices[-1]]])
        y = pendiente * (x - t0) + intercepto
        ax.plot(x, y, lw=3.1, color=COLORES[parametro], label=f"{parametro}: {t_api:.3f} s (API)")
        ax.axvspan(x[0], x[1], color=COLORES[parametro], alpha=0.055)
    ax.set(
        xlabel="Tiempo (s)",
        ylabel="Energía integrada relativa (dB)",
        title=f"{nombre} · Schroeder y regresiones, banda de 1000 Hz",
    )
    ax.set_ylim(-55, 3)
    ax.set_xlim(0, len(ir) / fs)
    ax.grid(alpha=0.2)
    ax.legend(loc="best", fontsize=9)
    fig.text(
        0.11,
        0.005,
        "Las rectas se reconstruyen con los tiempos del endpoint; "
        "el inicio se estima visualmente con el umbral experimental de 10%.",
        fontsize=8,
    )
    fig.tight_layout(rect=[0, 0.025, 1, 1])
    salvar_figura(fig, f"{cod}_01_schroeder_regresiones.png")


def grafica_filtros(ir: np.ndarray, fs: int, nombre: str, cod: str) -> None:
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11.5, 9.0))
    t = np.arange(len(ir)) / fs
    colores = plt.get_cmap("tab10").colors
    for j, fc in enumerate(BANDAS):
        sos = sps.butter(
            4, [fc / np.sqrt(2), fc * np.sqrt(2)], btype="bandpass", fs=fs, output="sos"
        )
        frecuencias, h = sps.sosfreqz(sos, worN=8192, fs=fs)
        # sosfiltfilt (ida y vuelta): ganancia efectiva |H|**2.
        db = 40 * np.log10(np.maximum(np.abs(h), 1e-10))
        ax1.plot(frecuencias, db, label=f"{fc} Hz", color=colores[j], lw=1.5)

        banda = filter_single_band(ir, fs, float(fc))
        env = apply_smoothing(banda, fs, method="hilbert")
        norm = max(float(np.max(env)), np.finfo(float).tiny)
        env_db = 20 * np.log10(np.maximum(env / norm, 1e-5))
        ax2.plot(t, env_db, label=f"{fc} Hz", color=colores[j], lw=1.0)

    ax1.set(
        xscale="log",
        xlim=(50, 9500),
        ylim=(-90, 4),
        xlabel="Frecuencia (Hz)",
        ylabel="Magnitud del filtro (dB)",
        title="Respuesta de los filtros por octava",
    )
    ax2.set(
        xlim=(0, len(ir) / fs),
        ylim=(-95, 5),
        xlabel="Tiempo (s)",
        ylabel="Envolvente normalizada (dB)",
        title="Envolvente de Hilbert por banda",
    )
    for a in (ax1, ax2):
        a.grid(alpha=0.25)
        a.legend(ncol=3, fontsize=9)
    fig.suptitle(f"{nombre} · procesamiento multibanda", fontsize=15)
    fig.tight_layout()
    salvar_figura(fig, f"{cod}_02_comparacion_filtros.png")


def comparar(params: dict, refs: dict, nombre: str) -> list[dict]:
    filas = []
    for parametro in (*PARAMS_NORMA, "D50"):
        for i, banda in enumerate(BANDAS):
            v = valor(params, parametro, banda)
            r = float(refs[parametro][i])
            dif = None if v is None else v - r
            if v is None:
                estado = "No calculado"
                umbral = None
            elif parametro == "D50":
                estado = "Informativo"
                umbral = None
            else:
                umbral = 1.0 if parametro == "C80" else min(0.10 * abs(r), 0.5)
                estado = "Cumple" if abs(dif) <= umbral else "Fuera de tolerancia"
            filas.append(
                {
                    "Recinto": nombre,
                    "Parametro": parametro,
                    "Banda_Hz": banda,
                    "RIR_API": v,
                    "REW": r,
                    "Diferencia_API_menos_REW": dif,
                    "Error_relativo_pct": (
                        100 * abs(dif) / abs(r) if dif is not None and r != 0 else None
                    ),
                    "Tolerancia": umbral,
                    "Estado": estado,
                }
            )
    return filas


def grafica_rew(filas: list[dict], nombre: str, cod: str) -> None:
    fig, axs = plt.subplots(2, 2, figsize=(12, 8.8))
    for ax, parametro in zip(axs.ravel(), PARAMS_NORMA, strict=True):
        grupo = [f for f in filas if f["Parametro"] == parametro]
        xs = np.arange(len(BANDAS))
        ref = np.array([f["REW"] for f in grupo], dtype=float)
        api = np.array(
            [np.nan if f["RIR_API"] is None else f["RIR_API"] for f in grupo], dtype=float
        )
        tolerancia = np.array([min(0.10 * abs(r), 0.5) if parametro != "C80" else 1 for r in ref])
        ax.fill_between(
            xs, ref - tolerancia, ref + tolerancia, color="#BBDAE5", alpha=0.38, label="Tolerancia"
        )
        ax.plot(xs, ref, "o--", lw=1.8, color="#206080", label="REW")
        ax.plot(xs, api, "s-", lw=1.8, color="#CE7843", label="RIR-API")
        for j, fila in enumerate(grupo):
            if fila["Estado"] == "Fuera de tolerancia":
                ax.scatter(j, api[j], s=130, marker="x", linewidths=2.3, c="#B12D34")
            elif fila["Estado"] == "No calculado":
                ax.text(j, ref[j], "None", ha="center", va="bottom", fontsize=8)
        cuenta = Counter(f["Estado"] for f in grupo)
        ax.set_title(f"{parametro}: {cuenta['Cumple']}/6 dentro de tolerancia")
        ax.set_xticks(xs, [str(x) for x in BANDAS])
        ax.set(xlabel="Banda de octava (Hz)", ylabel="dB" if parametro == "C80" else "s")
        ax.grid(alpha=0.2)
    axs[0, 0].legend(loc="best")
    fig.suptitle(f"{nombre} · validación RIR-API frente a REW", fontsize=15)
    fig.tight_layout()
    salvar_figura(fig, f"{cod}_03_validacion_rew.png")


def grafica_sintetica(data: dict) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 6.0))
    obj = [T60_OBJETIVO[b] for b in BANDAS]
    ax.plot(BANDAS, obj, "o--", color="#20242D", lw=2.4, label="T60 configurado")
    for nombre in ("EDT", "T20", "T30"):
        data_y = [
            np.nan
            if valor(data["parameters"], nombre, b) is None
            else valor(data["parameters"], nombre, b)
            for b in BANDAS
        ]
        ax.plot(BANDAS, data_y, "o-", color=COLORES[nombre], label=nombre, lw=2)
    ax.set_xscale("log", base=2)
    ax.set_xticks(BANDAS, [str(b) for b in BANDAS])
    ax.set(
        xlabel="Banda central (Hz)",
        ylabel="Tiempo (s)",
        title="RI sintética de 5 s · T60 esperado vs tiempos medidos por API",
    )
    ax.grid(alpha=0.24)
    ax.legend()
    fig.tight_layout()
    salvar_figura(fig, "sintetica_t60_conocido.png")


def texto_valor(v: float | None, unidad: str = "") -> str:
    return "None" if v is None else f"{v:.3f}{unidad}"


def tabla_matriz(params: dict, ref: dict) -> str:
    filas = [
        "| Parámetro / banda (Hz) | 125 | 250 | 500 | 1000 | 2000 | 4000 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for parametro in (*PARAMS_NORMA, "D50"):
        unit = "s" if parametro in ("EDT", "T20", "T30") else "dB" if parametro == "C80" else "%"
        for fuente, serie in (
            ("RIR-API", [valor(params, parametro, b) for b in BANDAS]),
            ("REW", ref[parametro]),
        ):
            filas.append(
                f"| {parametro} ({unit}) · {fuente} | "
                + " | ".join(texto_valor(x) for x in serie)
                + " |"
            )
    return "\n".join(filas)


def tabla_detallada(filas: list[dict]) -> str:
    res = [
        "| Parámetro | Banda (Hz) | RIR-API | REW | Δ (API−REW) | Tolerancia | Estado |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]
    for f in filas:
        fila_md = "| {Parametro} | {Banda_Hz} | {api} | {REW:.3f} | {dif} | {tol} | {Estado} |"
        res.append(
            fila_md.format(
                **f,
                api=texto_valor(f["RIR_API"]),
                dif=texto_valor(f["Diferencia_API_menos_REW"]),
                tol=texto_valor(f["Tolerancia"]),
            )
        )
    return "\n".join(res)


def resumen(filas: list[dict]) -> tuple[int, int, int, dict]:
    c = Counter(f["Estado"] for f in filas if f["Parametro"] in PARAMS_NORMA)
    por = {p: Counter(f["Estado"] for f in filas if f["Parametro"] == p) for p in PARAMS_NORMA}
    return c["Cumple"], c["Fuera de tolerancia"], c["No calculado"], por


def escribir_csv(ruta: Path, filas: list[dict]) -> None:
    with ruta.open("w", newline="", encoding="utf-8") as salida:
        writer = csv.DictWriter(salida, fieldnames=list(filas[0]))
        writer.writeheader()
        writer.writerows(filas)


def generar_documentacion(api: dict, refs: dict, comparaciones: dict, git: dict) -> None:
    res = [
        "## Validación M3 · Parámetros acústicos por banda",
        "",
        "### Objetivo y alcance",
        "",
        "Se completó la cadena de M1–M3 con la lectura de RI, filtrado en bandas de octava,",
        "integral de Schroeder, regresión lineal y estimación de EDT, T10, T20, T30, D50 y C80.",
        "La evaluación utiliza **la implementación que estaba activa al ejecutar el script**;",
        "el cálculo numérico se obtuvo mediante `POST /api/v1/acoustics/parameters` con",
        "`TestClient` de FastAPI (sin levantar servidor externo).",
        "",
        "**Versión evaluada:** rama `{}`; commit `{}`; cambios sin commit: **{}**.".format(
            git["rama"],
            git["commit"],
            "sin verificar"
            if git["cambios_sin_commit"] is None
            else "sí"
            if git["cambios_sin_commit"]
            else "no",
        ),
        "",
        "### Señales y método",
        "",
        "Se reutilizaron dos RI del MIT IR Survey",
        "(<https://mcdermottlab.mit.edu/Reverb/IR_Survey.html>),",
        "ya utilizadas en M2, sin modificar sus muestras originales:",
        "",
        "- **Hallway Elementary School (h042):**",
        "  `docs/m2/h042_Hallway_ElementarySchool_4txts.wav`,",
        "  32000 Hz y aproximadamente 1,994 s.",
        "- **Livingroom (h045):** `docs/m2/h045_Livingroom_4txts.wav`,",
        "  32000 Hz y aproximadamente 0,675 s.",
        "- **Sintética:** `generate_synthetic_ir(duration=5, fs=44100)`, con T60 configurado",
        "  por banda en `docs/m3/validar_m3.py` (semilla fija en el generador).",
        "",
        "Cada RI se analiza en 125, 250, 500, 1000, 2000 y 4000 Hz.",
        "Los intervalos de regresión de la curva de Schroeder son EDT: 0 a −10 dB,",
        "T10: −5 a −15 dB, T20: −5 a −25 dB y T30: −5 a −35 dB;",
        "el tiempo se extrapola mediante `−60 / pendiente`.",
        "Los resultados dependen de la referencia temporal elegida para el sonido directo,",
        "del filtrado, del ruido de fondo y de la linealidad del decaimiento.",
        "",
        "Los valores de REW son las **tablas A y B transcritas en el README de M2**.",
        "No se utilizaron los archivos `referencia_h042.json` y `referencia_h045.json` de M2",
        "como referencias REW: esos pertenecen a la API de la cátedra.",
        "",
        "### Criterios de evaluación",
        "",
        "EDT, T20 y T30: tolerancia de `min(10 % × |valor REW|, 0,5 s)`.",
        "C80: diferencia absoluta máxima de 1 dB. Las mediciones `None` cuentan como",
        "**no calculadas**, no como aciertos. D50 se informa frente a REW, pero sin",
        "veredicto de tolerancia porque la consigna no especifica un umbral para D50.",
        "T10 se calcula y exporta a JSON, pero no tiene referencia REW en estas tablas.",
        "",
        "### 1. Validación con RI sintética",
        "",
        "Se analizaron tiempos de reverberación conocidos por banda (segundos):",
        "",
        "| Banda (Hz) | T60 configurado | EDT API | T20 API | T30 API |",
        "|---:|---:|---:|---:|---:|",
    ]
    s = api["Sintética"]["parameters"]
    for b in BANDAS:
        res.append(
            f"| {b} | {T60_OBJETIVO[b]:.3f} | "
            + " | ".join(texto_valor(valor(s, p, b)) for p in ("EDT", "T20", "T30"))
            + " |"
        )
    res.extend(
        [
            "",
            "La RI sintética permite comprobar la recuperación de T20 y T30 frente a un",
            "tiempo configurado; EDT puede diferir por la estructura del decaimiento inicial.",
            "",
            "![RI sintética: T60 conocido](docs/m3/sintetica_t60_conocido.png)",
            "",
        ]
    )
    total_bien = total_fuera = total_none = 0
    for nombre, (cod, _wav) in RI_REALES.items():
        params = api[nombre]["parameters"]
        filas = comparaciones[nombre]
        bien, fuera, nulos, por = resumen(filas)
        total_bien += bien
        total_fuera += fuera
        total_none += nulos
        res.extend(
            [
                f"### 2. {nombre} ({cod}) — resultados por banda",
                "",
                tabla_matriz(params, refs[nombre]),
                "",
                f"**Resultado:** {bien}/24 comparaciones dentro de tolerancia; "
                f"{fuera} fuera y {nulos} `None`.",
                "",
                "| Parámetro | Dentro de tolerancia | Fuera | None |",
                "|---|---:|---:|---:|",
            ]
        )
        for p in PARAMS_NORMA:
            c = por[p]
            res.append(
                f"| {p} | {c['Cumple']}/6 | {c['Fuera de tolerancia']} | {c['No calculado']} |"
            )
        res.extend(
            [
                "",
                "#### Curva de Schroeder y regresiones (1000 Hz)",
                "",
                f"![Schroeder y ajustes {nombre}](docs/m3/{cod}_01_schroeder_regresiones.png)",
                "",
                "El gráfico muestra la curva de energía integrada y las rectas reconstruidas",
                "con los tiempos informados por el endpoint. **La detección de inicio y la",
                "normalización usadas para dibujar la figura son una reconstrucción diagnóstica**",
                "de la variante experimental (umbral del 10 %); la respuesta JSON del endpoint",
                "es la fuente de verdad para las tablas y el cumplimiento.",
                "",
                "#### Comparación de filtros por bandas",
                "",
                f"![Filtros por bandas {nombre}](docs/m3/{cod}_02_comparacion_filtros.png)",
                "",
                "Se muestra la respuesta en frecuencia de filtros Butterworth y la envolvente",
                "de Hilbert de las seis bandas de octava. La envolvente es descriptiva,",
                "no se usa para sustituir la energía cuadrática de Schroeder.",
                "",
                "#### Comparación RIR-API vs. REW",
                "",
                f"![Comparación contra REW {nombre}](docs/m3/{cod}_03_validacion_rew.png)",
                "",
                "La franja sombreada indica tolerancia según la consigna; las cruces",
                "rojas señalan mediciones fuera del intervalo de aceptación.",
                "",
                f"Tabla detallada de las 24 comparaciones: "
                f"[`docs/m3/{cod}_comparacion_detallada.md`](docs/m3/{cod}_comparacion_detallada.md).",
                "",
            ]
        )
    res.extend(
        [
            "### 3. Evaluación global y limitaciones",
            "",
            "Sobre **48** comparaciones evaluables (2 recintos × 6 bandas × 4 parámetros),",
            f"**{total_bien} cumplen**, **{total_fuera}** están fuera de tolerancia y",
            f"**{total_none}** no se calcularon.",
            "",
            "La integral de Schroeder y los tiempos de decaimiento T20/T30 muestran",
            "una buena concordancia en estas RI, pero EDT es sensible al instante",
            "directo y al comportamiento no lineal de los primeros 10 dB; C80 es",
            "sensible a la división de energía a 80 ms. Un R² bajo no demuestra por",
            "sí solo una medición imposible: el criterio experimental genera una",
            "advertencia y conserva el valor si hay rango dinámico, puntos y pendiente válidos.",
            "No se ajustaron parámetros para forzar coincidencia con REW y las",
            "discrepancias se publican explícitamente.",
            "",
            "**Alcance:** se documenta la conformidad frente a las tolerancias de la",
            "consigna en estos archivos de prueba; no constituye una certificación de",
            "conformidad de todas las mediciones posibles con ISO 3382.",
            "",
            "### 4. Reproducibilidad y pruebas",
            "",
            "Desde la raíz del repositorio, con el entorno configurado:",
            "",
            "```powershell",
            "python docs/m3/validar_m3.py",
            "python -m pytest -v",
            "python -m ruff check .",
            "```",
            "",
            "El script procesa los WAV de `docs/m2/` y escribe en `docs/m3/` los",
            "gráficos, tablas, JSON, CSV y este fragmento del README. No modifica",
            "ni los audios originales ni el algoritmo de los servicios.",
            "",
            "Para probar la API manualmente: `python -m uvicorn app.main:app --reload`",
            "y subir una RI desde `http://127.0.0.1:8000/docs`.",
            "",
            "**Revisión previa al merge:** ejecutar el script en la rama experimental",
            "y repetir tras incorporar el PR, conservando versión, fecha y resultados.",
            "",
        ]
    )
    (DESTINO / "seccion_readme_m3.md").write_text("\n".join(res), encoding="utf-8")
    evidencia = [
        "# Evidencia detallada · Validación M3",
        "",
        "Las referencias profesionales provienen de REW, no de la API de cátedra.",
        "El CSV incluye la diferencia firmada `RIR_API − REW`, el error relativo",
        "y la decisión de tolerancia. D50 es informativo y T10 no tiene referencia",
        "REW transcrita en M2.",
    ]
    for nombre, (_cod, _wav) in RI_REALES.items():
        evidencia += ["", f"## {nombre}", "", tabla_detallada(comparaciones[nombre])]
    evidencia += [
        "",
        "## Limitaciones",
        "",
        "El R² de la recta es un indicador de linealidad; no se convierte",
        "automáticamente en un certificado de validez. El instante directo",
        "es estimado mediante una heurística experimental. Los valores muy",
        "pequeños de EDT pueden producir errores relativos altos incluso",
        "cuando el error absoluto es de pocos milisegundos.",
        "",
    ]
    (DESTINO / "evidencia_m3.md").write_text("\n".join(evidencia), encoding="utf-8")


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    faltan = [
        str(M2 / nombre) for _cod, nombre in RI_REALES.values() if not (M2 / nombre).is_file()
    ]
    if faltan:
        raise FileNotFoundError("WAV faltantes en docs/m2: " + "; ".join(faltan))
    refs = json.loads((DESTINO / "referencias_rew.json").read_text(encoding="utf-8"))
    if tuple(refs["bandas_hz"]) != BANDAS:
        raise ValueError("Las frecuencias de referencias_rew.json no coinciden")
    git = estado_git()
    print(f"Validación desde rama {git['rama']} (commit {git['commit']})")
    print("POST /api/v1/acoustics/parameters (TestClient)")
    with TestClient(app) as cliente:
        api = {
            nombre: analizar_wav(cliente, M2 / archivo)
            for nombre, (_cod, archivo) in RI_REALES.items()
        }
        api["Sintética"] = generar_sintetica(cliente)
    comparaciones = {}
    for nombre, (cod, archivo) in RI_REALES.items():
        ir, fs = load_audio(M2 / archivo)
        grafica_schroeder(ir, fs, api[nombre], nombre, cod)
        grafica_filtros(ir, fs, nombre, cod)
        filas = comparar(api[nombre]["parameters"], refs[nombre], nombre)
        comparaciones[nombre] = filas
        grafica_rew(filas, nombre, cod)
        (DESTINO / f"{cod}_comparacion_detallada.md").write_text(
            tabla_detallada(filas) + "\n", encoding="utf-8"
        )
    grafica_sintetica(api["Sintética"])
    todas = [f for grupo in comparaciones.values() for f in grupo]
    escribir_csv(DESTINO / "comparacion_rew_m3.csv", todas)
    (DESTINO / "resultados_api_m3.json").write_text(
        json.dumps(
            {
                "generado_utc": datetime.now(UTC).isoformat(),
                "version_git": git,
                "resultados_endpoint": api,
                "t60_sintetica_objetivo_s": T60_OBJETIVO,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    generar_documentacion(api, refs, comparaciones, git)
    print("\nResumen por recinto (EDT/T20/T30/C80, 24 comparaciones cada uno):")
    for nombre in RI_REALES:
        bien, fuera, none, _ = resumen(comparaciones[nombre])
        print(f"  {nombre}: {bien}/24 cumple; {fuera} fuera; {none} None")
    print("\nListo: docs/m3/seccion_readme_m3.md y docs/m3/evidencia_m3.md")


if __name__ == "__main__":
    main()
