## Log de Desarrollo con Inteligencia Artificial (AI_LOG.md) — Milestone 2

### Información del Milestone
* **Fecha:** 4 de noviembre de 2026
* **Milestone:** Milestone 2 (M2) — Procesamiento de la Respuesta al Impulso (RI)
* **Herramienta utilizada:** Gemini

---

### Registro de Prompts Clave e Interacciones


#### Entrada 1: Generación del script de procesamiento multi-banda (`scripts/validate_m2.py`)
* **Consulta realizada (Prompt):**
  > *"Escribir un script en Python (`scripts/validate_m2.py`) que tome las RIs reales en formato `.wav` (`h042_Hallway_ElementarySchool_4txts.wav` y `h045_Livingroom_4txts.wav`) ubicadas en `docs/m2/`, las procese en las 6 bandas de octava normalizadas (125 Hz, 250 Hz, 500 Hz, 1 kHz, 2 kHz y 4 kHz) usando `filter_single_band` y `logarithmic_scale_conversion`, y guarde las gráficas comparativas en `docs/m2/`."*
* **Resultado obtenido:**
  * Código modular completo del script ejecutado como módulo (`uv run python -m scripts.validate_m2`) para evitar errores de importación
  * Generación automática de los archivos `val_multiband_h042_Hallway_ElementarySchool_4txts.png` y `val_multiband_h045_Livingroom_4txts.png`
* **Evaluación y aprendizaje:**
  * Se automatizó la creación de evidencias gráficas requeridas por la cátedra para todas las octavas de la norma IEC 61260 en un solo paso.

---

#### Entrada 2: Redacción de la sección de validación y tablas para el `README.md`
* **Consulta realizada (Prompt):**
  > *"Bien, ahí están las tablas y los gráficos. Hagamos el análisis de los gráficos para poner en el README y su ruta (todos los gráficos están en `docs/m2/`). Las tablas de datos numéricos extraídas de REW (Room EQ Wizard) pásalas a formato texto en Markdown."*
* **Resultado obtenido:**
  * Transcripción completa en Markdown de los parámetros acústicos ISO 3882 (EDT, T20, T30, C50, C80, D50, TS) extraídos de REW para las 6 octavas.
  * Texto explicativo estructurado enlazando secuencialmente cada figura y tabla resumen comparativa entre la API y el software comercial.
* **Evaluación y aprendizaje:**
  * Facilitó el volcado directo de los resultados de validación requeridos en la rúbrica del README sin necesidad de redactar informes en PDF externos.