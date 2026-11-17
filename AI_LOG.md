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


## Milestone 3 — Organización y planificación del desarrollo

### Información de la interacción

- **Fecha:** 16 de noviembre de 2026.
- **Herramienta utilizada:** ChatGPT (OpenAI).
- **Milestone:** M3 — Producto final.
- **Objetivo:** Revisión y organización de las issues de desarrollo.

### Uso de inteligencia artificial

Se utilizó ChatGPT como herramienta de asistencia para revisar la organización de las tareas correspondientes a M3 y mejorar la documentación de las issues del repositorio.

Se buscó agrupar cada servicio de procesamiento con su endpoint, schema y tests asociados, evitando dividir una misma funcionalidad en múltiples tareas independientes.

### Ejemplo de consulta realizada

> "Me gustaría crear issues donde las funciones y sus endpoints estén en lo mismo, explicando qué se hizo y sus criterios de aceptación. Dividilo entonces en una issue con función + sus endpoints."

### Resultado obtenido

La herramienta propuso reorganizar las siguientes issues:

- **#9 — Suavizado:** `apply_smoothing` junto al endpoint `/utils/smoothing`.
- **#10 — Integral de Schroeder:** `apply_schroeder_integral` junto al endpoint `/utils/schroeder`.
- **#11 — Parámetros acústicos:** `linear_regression`, `calculate_parameters_from_ir` y el endpoint `/acoustics/parameters`.

También se identificó la necesidad de mantener separada la implementación opcional de Lundeby (#50) y de documentar la validación final (#51).

Para cada issue se generó una descripción de las tareas de implementación y una lista de criterios de aceptación relacionados con el funcionamiento de los servicios, los schemas, los endpoints y los tests automatizados.

### Verificación y evaluación

Las propuestas se contrastaron con la especificación oficial de M3 y con las funciones y tests existentes en el repositorio.

La herramienta se utilizó para organizar y redactar documentación, no para implementar o ejecutar las funcionalidades.

La aceptación definitiva de los cambios, su implementación y la comprobación de los tests quedan a cargo de los integrantes del grupo.