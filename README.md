# Instrumentación Biomédica — Práctica EMG

Repositorio de apoyo para la práctica de electromiografía del Módulo 2 de
Instrumentación Biomédica.

## Objetivo general

Comparar tres fuentes de señal EMG utilizando un procedimiento común de
documentación, procesamiento y análisis:

1. **Vernier** — adquisición experimental de EMG superficial.
2. **Sensor analógico y Arduino** — acondicionamiento, validación y adquisición
   digital de la señal.
3. **PhysioNet** — análisis de registros documentados de EMG de aguja.

El objetivo no es decidir cuál sistema es "mejor", sino identificar qué
diferencias pueden explicarse por el origen de la señal, la colocación y
separación de los electrodos, la cadena de acondicionamiento, la frecuencia de
muestreo y el procesamiento.

## Pregunta experimental

¿Cómo cambian la amplitud, la envolvente y el contenido frecuencial de la señal
EMG al modificar la separación entre los electrodos?

Esta variable se estudia únicamente en las adquisiciones superficiales con
Vernier y con el sensor analógico. Los registros de PhysioNet fueron adquiridos
con electrodo de aguja y se utilizan para aplicar el mismo procesamiento, no
para estudiar la separación interelectródica.

## Flujo de trabajo

```text
Vernier ───────────────┐
                      │
Sensor + interfaz      ├── procesamiento común ── comparación final
       + Arduino ──────┤
                      │
PhysioNet ─────────────┘
```

En la estación con Arduino, cada equipo deberá proponer una interfaz que adapte
la salida del sensor al intervalo permitido por el ADC. El diseño debe
justificarse a partir de los requisitos de amplitud, polaridad, offset, ancho de
banda, protección y alimentación. La interfaz se valida primero con generador y
osciloscopio, sin conectar al voluntario, y sólo después se utiliza para la
adquisición digital.

## Qué se documenta

Para cada fuente se registran, cuando estén disponibles:

- identificación del sistema y del registro;
- músculo, postura, carga y condición experimental;
- tipo, posición, orientación y separación de los electrodos;
- frecuencia de muestreo, unidades y duración del segmento;
- ganancia, offset, filtros y referencia del ADC;
- intervalo analizado y criterio utilizado para seleccionarlo;
- señal cruda, rectificada, envolvente y RMS móvil;
- RMS, MAV, iEMG y amplitud pico a pico;
- PSD, potencia integrada, frecuencia media y frecuencia mediana;
- saturación, ruido, artefactos y limitaciones de la medición.

## Estructura del repositorio

```text
instrumentacion-biomedica-emg/
├── README.md
├── requirements.txt
├── environment.yml
├── .gitignore
├── LICENSE
├── CITATION.cff
│
├── arduino/
│   └── emg_arduino/
│       └── emg_arduino.ino
│
├── scripts/
│   ├── captura_arduino.py
│   ├── analiza_csv.py
│   ├── analiza_physionet.py
│   ├── comparar_resultados.py
│   └── emg_core.py
│
├── docs/
│   ├── GUIA_ESTACIONES.md
│   └── PUBLICACION_GIT.md
│
├── config/
│   └── metadatos_plantilla.json
│
├── informes/
│   └── equipoXX.md
│
├── figuras/
├── resultados/
└── datos/
    ├── demo/
    └── crudos/
```

## Instalación

### Opción 1 — pip

```bash
python -m pip install -r requirements.txt
```

### Opción 2 — Conda

```bash
conda env create -f environment.yml
conda activate emg-instrumentacion
```

## Comprobación inicial

Antes de trabajar con los equipos puede comprobarse la instalación mediante
señales sintéticas:

```bash
python scripts/ejecutar_demo.py
```

Este comando guarda figuras y tablas de prueba en `resultados/demo/`.

## Uso durante las estaciones

### Vernier o archivo experimental en CSV

Exporte el registro desde Graphical Analysis o Logger Pro y guárdelo localmente
en `datos/crudos/`. Después ejecute:

```bash
python scripts/analiza_csv.py datos/crudos/vernier.csv \
  --source Vernier --spacing-mm 20 --signal-unit mV \
  --output-dir resultados/equipo01
```

El mismo programa se utiliza para analizar el CSV obtenido con Arduino.

### Adquisición con Arduino

Después de validar la interfaz y confirmar que su salida permanece dentro del
intervalo permitido por el ADC:

```bash
python scripts/captura_arduino.py \
  --port COM3 --baud 500000 --seconds 30 --live-plot \
  --spacing-mm 20 --output datos/crudos/arduino_d20.csv
```

Antes de interpretar la FFT o la PSD debe identificarse si la salida del sensor
corresponde a EMG crudo, señal rectificada o envolvente.

### PhysioNet

El siguiente programa descarga y analiza los registros de la base *Examples of
Electromyograms*:

```bash
python scripts/analiza_physionet.py \
  --start 0 --duration 2 \
  --output-dir resultados/equipo01/physionet
```

Fuente: <https://physionet.org/content/emgdb/1.0.0/>.

### Comparación final

```bash
python scripts/comparar_resultados.py resultados/equipo01 \
  --output-dir resultados/equipo01/comparacion
```

Los programas son herramientas de adquisición, visualización y análisis. La
práctica evalúa principalmente las decisiones de instrumentación, la
trazabilidad del procedimiento y la interpretación de los resultados.

## Interpretación de las variables

RMS, MAV, envolvente y PSD describen la actividad eléctrica registrada. No son
mediciones directas de fuerza ni de potencia mecánica. Una amplitud mayor
tampoco implica automáticamente mayor activación muscular, porque la señal
depende de la geometría de los electrodos, el tejido, la cancelación espacial,
el crosstalk y la cadena de adquisición.

## Datos fisiológicos

Los archivos fisiológicos crudos obtenidos de estudiantes deben permanecer en
`datos/crudos/` y **no se incluyen en el repositorio público**.

No deben publicarse nombres, matrículas, fotografías identificables ni otros
datos personales. En Git se conservan el código, los parámetros, las ventanas
analizadas, los resultados derivados, las figuras y las conclusiones.

## Seguridad y alcance

Este material tiene fines docentes y no permite establecer diagnósticos. La
adquisición en personas sólo debe realizarse con el esquema de alimentación,
aislamiento y conexión autorizado por el responsable del laboratorio.

La validación con generador y osciloscopio se realiza con el voluntario
completamente desconectado. Nunca debe eliminarse la conexión de tierra de un
osciloscopio para intentar que el instrumento quede flotante.

## Control de versiones

Git permite conservar cómo evoluciona el trabajo experimental. Un historial
posible sería:

```text
Documenta protocolo y parámetros de adquisición
Agrega resultados de Vernier
Agrega diseño y validación de la interfaz
Agrega adquisición y análisis con Arduino
Agrega comparación con PhysioNet
Integra discusión y conclusiones finales
```

Así se conserva no sólo el resultado final, sino también **cómo se construyó**.

## Referencias principales

- Webster, J. G., y Nimunkar, A. J. (eds.). *Medical Instrumentation:
  Application and Design*, 5.a ed., Wiley, 2020.
- Husar, P., y Gašpar, G. *Electrical Biosignals in Biomedical Engineering*.
  Springer, 2023.
- PhysioNet. *Examples of Electromyograms*, versión 1.0.0.
- Vernier. *EKG Sensor User Manual*, EKG-BTA.

## Licencias

El código se distribuye con licencia MIT. Los datos de PhysioNet conservan su
propia licencia y atribución; los programas los descargan desde la fuente
oficial y no los redistribuyen dentro de este repositorio.
