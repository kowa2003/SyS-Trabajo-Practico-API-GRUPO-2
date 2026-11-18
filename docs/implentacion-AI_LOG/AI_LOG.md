# Log de Desarrollo con Inteligencia Artificial (AI_LOG.md)

## Milestone 0 — Arquitectura y configuración inicial

### Información del milestone

- **Período:** Octubre de 2026.
- **Herramienta utilizada:** ChatGPT (OpenAI).
- **Objetivo:** Asistencia en la configuración del entorno de desarrollo y revisión de la documentación de arquitectura.
- **Integrante:** Joaquin Vargas
### Entrada 1: Diagnóstico de problemas con Uvicorn y uv

**Consulta realizada (7/10/2026):**

> "uv run python -m uvicorn app.main:app --reload" con este codigo funciona, pero antes funcionaba co el codigo que te mande al pricipio de una. Yo no cambie la carpeta de lugar. Porque le pinta esa ahora?

También se consultó:

> sigue teniendo el mismo error. Yo estoy usando la libreria "git" para trabajar en un repositorio en conjunto, puede ser que alguien haya subido algo al repositorio y que por eso deje de funcionar uv?

**Resultado obtenido:**

- Se analizaron posibles causas del error de ejecución de Uvicorn en Windows.
- Se explicó la diferencia entre ejecutar directamente el comando `uvicorn` y utilizar `python -m uvicorn`.
- Se revisó conceptualmente la relación entre el entorno virtual, las dependencias administradas por `uv` y los archivos del repositorio.

**Verificación y aprendizaje:**

Se comprobó que la API podía ejecutarse utilizando `uv run python -m uvicorn app.main:app --reload`.

La interacción permitió comprender mejor el funcionamiento del entorno virtual y distinguir problemas de ejecución local de posibles modificaciones del repositorio.

### Entrada 2: Revisión del diagrama de arquitectura

**Consulta realizada (28/10/2026, revisión posterior de M0):**

> esta bueno lo que hiciste, pero intenta que sea más parecido al que ya esta en el README no quiero que sea suuuuper especifico en el sentido de como va la señal. Fijate el que esta en el readme, hasta es mucho más didactivo y entendible que el choclazo que acabas de hacer.

**Resultado obtenido:**

- Se utilizó ChatGPT para revisar la presentación del diagrama de arquitectura.
- Se solicitó simplificar el nivel de detalle y mantener una representación más didáctica de los componentes de la API.
- Se priorizó explicar la organización del sistema sin representar innecesariamente cada operación interna del procesamiento de señales.

**Verificación y aprendizaje:**

La propuesta generada inicialmente por IA resultó demasiado detallada. Se revisó críticamente y se solicitó una alternativa más cercana al diagrama original del README.

Esta interacción permitió reconocer que una documentación técnicamente detallada no necesariamente es la más clara para comunicar la arquitectura de un proyecto.

---

## Milestone 1 — Generación de señales y reproducción/grabación

### Información del milestone

- **Período:** Octubre de 2026.
- **Herramienta utilizada:** ChatGPT (OpenAI).
- **Objetivo:** Asistencia durante el desarrollo, las pruebas y la documentación de los servicios de generación y reproducción/grabación de audio.
- **Integrante:** Joaquin Vargas

### Entrada 1: Validaciones del Sine Sweep y schemas de FastAPI

**Consulta realizada (22/10/2026):**

> che chatgpt ahi corri mi api, tengo una duda. Yo en mi schema tengo este codigo. Cuando abro mi API e intento ejecutar poniendo que mi f1= 1 no me deja, lo mismo si intento que f2= sea mayor que 20000

**Resultado obtenido:**

- Se analizaron las restricciones de frecuencia definidas en el schema de entrada.
- Se explicó cómo Pydantic aplica los límites de validación sobre los parámetros enviados desde Swagger.
- Se revisó la relación entre los valores permitidos, el generador de sine sweep y las pruebas automatizadas.

**Verificación y aprendizaje:**

Se realizaron pruebas desde la API para observar el comportamiento de los parámetros de entrada.

La interacción permitió comprender que las restricciones del schema deben estar alineadas con las condiciones de funcionamiento del servicio y con sus tests.

### Entrada 2: Prueba de play_and_record y funcionamiento de Swagger

**Consulta realizada (24/10/2026):**

> y la funcion play and record como se puede probar en el swagger?

Posteriormente se consultó:

> recien ejecute el codigo de python para comprobar si funciona el servicio play_and_record. En data quedo la grabacion_m1. Eso tiene que estar para la entrega? osea deberia subirlo al main no?

**Resultado obtenido:**

- Se explicó la diferencia entre probar servicios expuestos mediante endpoints HTTP y ejecutar directamente funciones que interactúan con dispositivos de audio.
- Se brindó asistencia para realizar una prueba local de reproducción y grabación.
- Se discutió cómo conservar las evidencias relevantes para la entrega sin incorporar archivos innecesarios al repositorio.

**Verificación y aprendizaje:**

Se ejecutó una prueba real de `play_and_record` y se obtuvo el archivo de grabación correspondiente.

Esta prueba permitió comprobar el funcionamiento del servicio en una situación distinta de los tests automatizados, utilizando dispositivos físicos de audio.

### Entrada 3: Documentación y evidencias de la grabación real

**Consulta realizada (28/10/2026):**

> bien, de la parte de los de grabación de la grabación real de la API quiero que hagas la misma explicacion pero en vez de guardar los archivos en data quiero que se guarden en la carpeta docs/m1, es posible?

También se realizó la siguiente consulta:

> che, cuando hago el comando de uv run python -m docs.m1.prueba_grabacion no pasa nada

**Resultado obtenido:**

- Se brindó asistencia para organizar las evidencias de grabación dentro de `docs/m1/`.
- Se revisó el procedimiento de ejecución del script de prueba real.
- Se analizaron problemas relacionados con la ejecución del módulo de Python.
- Se trabajó sobre la documentación de los dispositivos, canales, frecuencia de muestreo y configuración de grabación.

**Verificación y aprendizaje:**

Se realizaron comprobaciones locales del script y de la generación de archivos de evidencia.

La interacción permitió mejorar la reproducibilidad de las pruebas y comprender la importancia de documentar las condiciones reales bajo las cuales se verificó un servicio de audio.

### Entrada 4: Documentación técnica y calidad del código

**Consulta realizada (octubre de 2026):**

> a que se refiere con docstrings y type hints?

**Resultado obtenido:**

- Se explicó cómo utilizar docstrings para documentar el propósito, los parámetros y los resultados de las funciones.
- Se explicó el uso de type hints para indicar los tipos de entrada y salida.
- Se relacionaron estos elementos con los requisitos de documentación y mantenimiento del proyecto.

**Verificación y aprendizaje:**

Se revisó la documentación de las funciones implementadas y su relación con los criterios de calidad solicitados por la cátedra.

Esta interacción facilitó la comprensión de buenas prácticas de documentación en Python.

### Entrada 5: Cargar imagen en una rama de validacion.

> "puse el archivo de audio digital en REW y en la pestaña me de espectograma sale eso, entonces ahora tengo que subir la validacion a git hub, haciendo el agregado de imagen en una rama de validacion, como hago paso a paso?"

**Resultado obtenido:**

Para subir el espectrograma del sine sweep a GitHub y lograr que se visualice correctamente en el README.md, el proceso se resumió en guardar la gráfica en escala logarítmica dentro de la carpeta docs/m1/ (sin espacios ni mayúsculas inconsistentes en el nombre del archivo), crear una nueva rama de validación (git checkout -b ...), confirmar los cambios con git add y git commit, y publicarlos con git push. Finalmente, para que las imágenes se renderizaran en el documento y no aparecieran rotas o como enlaces simples, fue necesario agregar explícitamente las rutas relativas dentro del README.md anteponiendo el signo de exclamación (![Descripción](docs/m1/archivo.png)) bajo sus respectivos subtítulos.

**Verificación y aprendizaje:**

-Flujo de trabajo en ramas.
-Utilizacion de comandos git.

### Entrada 6: Generar funcion Play_and_record

* **IA UTILIZADA**: Gemini
* **Integrante:** Agustin Quaglia

**Consulta realizada (Prompt):**

> Tengo que generar una funcion en python que sea para grabar y reproducir a la vez, se va a reproducir y grabar un sine sweep y un ruido rosa. Esto lo estamos trabajando con un repositorio y github entre 4 amigos, donde deberia codear la funcion y los test que pasa. Ahi adjunto parte de la consigna y foto de mi VS CODE con el repositorio descargado localmente. (Adjunte fotos)

>adjunto screen del repositorio local mio de vs code y como aparece el servicio de play_and_record y los test que ya aparecen

**Resultado obtenido:**

- Ubicación en el repositorio y flujo colaborativo: Se identificó que la implementación corresponde al módulo app/services/audio_io.py y su validación automática se encuentra en tests/test_generacion.py (específicamente en test_play_and_record_shape). Para trabajar entre los 4 integrantes sin generar conflictos, se estableció trabajar en una rama dedicada por tarea (feature/play_and_record).

- Estructura de play_and_record(signal, fs, record_duration): Se diseñó la función cumpliendo las especificaciones del servicio:   

Control de duración y márgenes: Validación de que record_duration sea mayor o igual a la duración de la señal (ValueError en caso contrario) y agregado de silencio inicial (pre-roll para compensar latencia) y final (post-roll) hasta alcanzar exactamente int(record_duration * fs) muestras.   

Compatibilidad 1D y 2D: Manejo de señales mono (1D) y estéreo/multicanal (2D con forma (muestras, canales)).   

Importación perezosa y manejo de dispositivos: Inclusión de import sounddevice as sd dentro de la función —y no al inicio del archivo— junto con un bloque try/except que captura la ausencia de interfaz de audio y lanza un RuntimeError con un mensaje descriptivo.

**Verificación y aprendizaje:**

- Acondicionamiento de señales en NumPy: Manejo de arreglos 1D (mono) y 2D (estéreo) aplicando relleno de ceros (pre-roll para compensar latencia y post-roll para cola de reverberación) hasta alcanzar exactamente int(record_duration * fs) muestras.

- Pruebas automatizadas y manejo de errores: Uso de importación perezosa de sounddevice dentro de la función para permitir su simulación con monkeypatch en pytest, validando tipos de retorno, excepciones ante fallos de dispositivo (RuntimeError) y ejecución consistente del entorno mediante uv run pytest -v.



### Entrada 7: Implementación de la generación de ruido rosa (generate_pink_noise)

* **IA UTILIZADA:** Claude (Anthropic) 
* **Integrante:** Rodrigo Sanchez Tejerina

**Consulta realizada:**

Se solicitó asistencia para comprender cómo implementar una función de generación de ruido rosa, ya que inicialmente no se tenía claro qué método utilizar.

**Resultado obtenido:**

Se propuso generar ruido blanco y transformarlo al dominio de la frecuencia mediante rfft.

Se explicó cómo aplicar una ponderación proporcional a (1/\sqrt{f}) para obtener el comportamiento espectral del ruido rosa.

Se propuso volver al dominio temporal mediante irfft y normalizar posteriormente la señal.

La estrategia estaba contemplada en el docstring de la función.

**Verificación y aprendizaje:**

Se ejecutaron los tests de test_generacion.py.

Se analizó el espectro de la señal generada utilizando Audacity.

Se verificó aproximadamente una pendiente de -10 dB/década (≈ -3 dB/octava).

Los resultados de la validación quedaron documentados en docs/m1/.

La implementación pasó las pruebas y produjo un espectro compatible con el comportamiento esperado del ruido rosa.

### Entrada 8: Implementación del endpoint de ruido rosa

* **IA UTILIZADA:** Claude (Anthropic) 
* **Integrante:** Rodrigo Sanchez Tejerina

**Consulta realizada:**

Se solicitó asistencia para desarrollar el schema, el router y registrar el endpoint de generación de ruido rosa en main.py.

Resultado obtenido:

Se propuso la estructura de PinkNoiseRequest.

Se desarrolló el endpoint POST /api/v1/signals/pink-noise.

Se utilizó wav_response para devolver la señal generada en formato WAV.

Se indicó cómo registrar el router correspondiente en main.py.

**Verificación y aprendizaje:**

Se probó el endpoint desde Swagger (/docs).

Se comprobó una respuesta HTTP 200 con un archivo WAV válido.

Se verificó que una duración negativa generara HTTP 422.

Se ejecutó el test automatizado test_signals_pink_noise_endpoint.

La interacción permitió comprender la relación entre los schemas de entrada, los routers de FastAPI y la respuesta de audio del servicio.

### Entrada 9: Validación espectral del ruido rosa mediante Audacity

* **IA UTILIZADA:** Claude (Anthropic) 
* **Integrante:** Rodrigo Sanchez Tejerina

**Consulta realizada:**

Se solicitó orientación para medir y comprobar la pendiente del espectro de frecuencias del ruido rosa generado.

Resultado obtenido:

Se proporcionaron indicaciones para visualizar el espectro de frecuencias en Audacity.

Se explicó cómo analizar los niveles en decibelios y comprobar el comportamiento espectral esperado.

Limitaciones y correcciones:

Inicialmente, la IA indicó que aumentar el tamaño de la FFT suavizaría la curva del espectro. Al realizar las pruebas se comprobó que esta explicación no era correcta: aumentar el tamaño de la FFT proporciona mayor resolución frecuencial, por lo que puede mostrar más variaciones en el espectro.

**Verificación y aprendizaje:**

Se contrastaron las indicaciones con las mediciones realizadas en Audacity y se corrigió la interpretación inicial.

Esta interacción permitió comprender mejor la relación entre el tamaño de la FFT, la resolución frecuencial y la visualización del espectro.
---

## Milestone 2

### Información del Milestone
* **Fecha:** 4 de noviembre de 2026
* **Milestone:** Milestone 2 (M2) — Procesamiento de la Respuesta al Impulso (RI)
* **Herramienta utilizada:** Gemini
* **Integrante:** Agustin Quaglia
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

---

#### Entrada 3: Generación del codigo del servicio logarithmic_scale_conversion(signal)

* **IA UTILIZADA:** Gemini
* **Integrante:** Agustin Quaglia

* **Consulta realizada (Prompt):**
  > para la aplicacion que venimos desarrollando de respuesta al impulso, tengo que hacer la funcion de convertir a escala logarimitca la señal, y me da esta data (adjunte imagenes de las especificaciones de la funcion que aparecian en la web de guia)

* **Resultado obtenido:**
  * Se obtuvo la implementación vectorizada en NumPy de la función para convertir la amplitud de la señal a escala logarítmica en decibelios, normalizando respecto al valor pico absoluto para que el máximo de la señal quede referenciado en cero decibelios.
  * Se incorporó protección numérica para evitar divisiones por cero y valores indeterminados (como infinitos negativos) ante muestras silenciosas, garantizando que el arreglo resultante sea válido para las respuestas JSON de la API.

* **Evaluación y aprendizaje:**
  * Se reforzó la importancia de contemplar casos borde en señales reales (como tramos de silencio digital o rellenos con ceros), ya que un logaritmo sin un límite inferior genera errores de serialización en el endpoint.
  * Si bien la herramienta agilizó la escritura del código en NumPy, fue clave aplicar criterio acústico para definir el umbral inferior: fijar el piso en `-120 dB` permite aprovechar el rango dinámico de equipamiento e interfaces de grabación profesionales (de 24 bits) sin truncar prematuramente las colas de decaimiento de la sala.
  * Asimismo, se auditó el código generado para asegurar que se aplicara el factor de escala correspondiente a magnitudes de amplitud o presión, y no el utilizado para energía o potencia.

### Entrada 4: Validación espectral del ruido rosa mediante Audacity

* **IA UTILIZADA:** Claude (Anthropic) 
* **Integrante:** Rodrigo Sanchez Tejerina

**Consulta realizada:**

Se solicitó asistencia para comprender cómo implementar el filtro de bandas de octava a partir del docstring y los tests existentes, así como desarrollar el endpoint correspondiente para procesar archivos de audio.

**Resultado obtenido:**

Se propuso una implementación del filtro Butterworth pasabanda utilizando butter(output="sos") y sosfiltfilt.

Se incorporó una validación de frecuencia de Nyquist para evitar configuraciones de filtrado inválidas.

Se propuso una estructura de endpoint que recibe archivos mediante UploadFile.

Se contempló el manejo de archivos inválidos mediante respuestas HTTP 422.


**Verificación y aprendizaje:**

SSe ejecutaron los tres tests de TestFilterSingleBand.

Se ejecutaron los tests correspondientes al endpoint.

Se realizaron las verificaciones de Ruff.

Durante la implementación se profundizó en el funcionamiento de sosfiltfilt, que realiza un filtrado hacia adelante y hacia atrás.

Se comprendió que ambas pasadas modifican la respuesta en magnitud: una atenuación de aproximadamente -3 dB en los bordes del Butterworth de una pasada pasa a ser aproximadamente -6 dB en el filtrado bidireccional. Este procedimiento permite obtener fase cero, aunque puede producir efectos transitorios en los extremos de la señal.
---


## Milestone 3 — Organización y planificación del desarrollo

### Información de la interacción

- **Fecha:** 16 de noviembre de 2026.
- **Herramienta utilizada:** ChatGPT (OpenAI).
- **Milestone:** M3 — Producto final.
- **Objetivo:** Revisión y organización de las issues de desarrollo.
- **Integrante:** Joaquin Vargas

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

### Implementación del servicio de suavizado y su endpoint

**Herramienta:** ChatGPT (OpenAI).

**Objetivo:** Asistencia para implementar `apply_smoothing` y el endpoint `/api/v1/utils/smoothing`.

**Uso de IA:**

Se utilizó ChatGPT para comprender los métodos de suavizado mediante transformada de Hilbert y media móvil RMS, proponer la implementación en Python y desarrollar el endpoint FastAPI con sus correspondientes schemas Pydantic.

La herramienta también brindó asistencia para corregir advertencias del linter Ruff relacionadas con el uso de `Annotated` y `StrEnum`.

**Verificación realizada:**

- Se ejecutaron los tests del servicio, obteniendo 3 pruebas satisfactorias.
- Se comprobó el test automatizado del endpoint.
- Se realizaron pruebas manuales desde Swagger utilizando una respuesta al impulso sintética.
- Se compararon los resultados de ambos métodos y se verificó el manejo de entradas inválidas mediante HTTP 422.

**Evaluación:**

La asistencia permitió completar la implementación y comprender las diferencias entre ambos métodos. Los resultados fueron comprobados mediante pruebas locales, sin asumir que el código generado era correcto únicamente por provenir de IA.


### Resultado obtenido

La herramienta propuso reorganizar las siguientes issues:

- **#9 — Suavizado:** `apply_smoothing` junto al e
Milestone 3 — Análisis acústico y producto final

### Información del milestone 3

* **IA UTILIZADA:** ChatGPT (OpenAI) 
* **Integrante:** Rodrigo Sanchez Tejerina
* **Objetivo:** Asistencia en la implementación de los cálculos de parámetros acústicos según ISO 3382 y el desarrollo del endpoint principal de análisis.

### Entrada 1: Implementación de los parámetros acústicos y el endpoint de análisis

**Consulta realizada:**
Se solicitó asistencia para implementar los cálculos acústicos de acuerdo con ISO 3382 y desarrollar el endpoint POST /api/v1/acoustics/parameters.

También se consultó sobre los fundamentos de la regresión lineal, la curva de Schroeder y las relaciones de energía utilizadas para obtener los parámetros acústicos.

**Resultado obtenido:**

Se propuso una implementación de linear_regression mediante mínimos cuadrados, incluyendo pendiente, intercepto y coeficiente de determinación R².

Se brindó asistencia para implementar calculate_parameters_from_ir.

Se desarrollaron propuestas de funciones auxiliares para estimar el rango dinámico, calcular tiempos de reverberación y obtener D50 y C80.

Se propuso la estructura del schema BandAnalysisResponse.

Se desarrolló la estructura del router acoustics.py y se indicó cómo registrarlo en main.py.

Se explicaron conceptos relacionados con las bandas de octava, la frecuencia de Nyquist y el manejo de parámetros no calculables mediante None.

**Verificación y aprendizaje:**:

Se realizaron las siguientes comprobaciones:

Ejecución de los tests de tests/test_analisis.py y tests/test_api.py.

Ejecución de la suite completa mediante uv run pytest -v, obteniendo 51 tests aprobados.

Ejecución de uv run ruff check app tests, obteniendo All checks passed!.

Ejecución de uv run ruff format --check app tests, obteniendo 26 files already formatted.

Verificación del endpoint desde Swagger, comprobando que estuviera registrado y recibiera archivos WAV correctamente.

**Depuración:**

Se utilizó ChatGPT para interpretar errores de pytest, distinguir entre XPASS, XFAIL y FAILED, corregir problemas de importación y registro del router y solucionar advertencias de Ruff.

Limitaciones y revisiones posteriores:

Durante una comparación preliminar con REW se detectó que algunos parámetros, especialmente EDT, podían devolver None, aunque T30 presentara un resultado cercano al de referencia.

También se identificó un umbral de R² de 0.99 que podía descartar regresiones válidas. La sugerencia de IA de utilizar ese umbral fue revisada y cuestionada.

A partir de estas observaciones se comenzó a investigar la detección del instante de llegada directa y la normalización de la integral de Schroeder, para evitar tomar automáticamente la primera muestra del archivo como referencia temporal.

Evaluación y criterio propio:

La asistencia permitió avanzar en la implementación y comprender los fundamentos de los cálculos acústicos. Sin embargo, no se consideró que la aprobación de los tests fuera suficiente para garantizar la precisión de los resultados.

La comparación con REW permitió identificar aspectos que requieren validación adicional sobre respuestas al impulso reales.