# Práctica de electromiografía: Vernier, Arduino y PhysioNet

Repositorio para las estaciones de la sesión de electromiografía de
Instrumentación Biomédica. El objetivo es comparar cómo la adquisición, la
separación interelectródica y el procesamiento modifican las variables obtenidas
de una señal EMG.

## Pregunta de trabajo

¿Cómo cambian la amplitud, la envolvente y el contenido frecuencial de la señal
EMG al modificar la separación entre los electrodos?

La separación sólo puede modificarse en las estaciones de adquisición
superficial con Vernier y Arduino. Los registros de PhysioNet ya fueron
adquiridos con electrodo de aguja; allí se aplica el mismo procesamiento para
comparar señales, sin atribuir las diferencias a la separación interelectródica.

## Contenido

```text
instrumentacion-biomedica-emg/
├── arduino/emg_arduino/       Programa de adquisición analógica
├── config/                    Plantilla de metadatos
├── datos/demo/                Señales sintéticas sin datos personales
├── datos/crudos/              Datos locales excluidos de Git
├── docs/                      Guías de estaciones y publicación
├── figuras/                   Figuras seleccionadas para la entrega
├── informes/                  Plantilla del informe del equipo
├── resultados/                Tablas y resultados derivados
├── scripts/                   Captura, análisis y comparación
├── tests/                     Pruebas automáticas básicas
├── environment.yml            Entorno Conda
└── requirements.txt           Dependencias para pip
```

## Instalación

### Opción A: Conda

```bash
conda env create -f environment.yml
conda activate emg-instrumentacion
```

### Opción B: entorno virtual y pip

En Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

En Linux o macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Comprobación sin equipo

El siguiente comando genera tres señales sintéticas, ejecuta el procesamiento y
guarda figuras y tablas en `resultados/demo/`:

```bash
python scripts/ejecutar_demo.py
```

## Estación A: Vernier

1. Exportar desde Graphical Analysis o Logger Pro un CSV con tiempo y potencial.
2. Guardarlo localmente dentro de `datos/crudos/`. Esta carpeta no se publica.
3. Ejecutar, por ejemplo:

```bash
python scripts/analiza_csv.py datos/crudos/vernier_d20.csv \
  --source Vernier \
  --condition contraccion_carga_constante \
  --spacing-mm 20 \
  --subject-code S01 \
  --signal-unit mV \
  --output-dir resultados/equipo01
```

El programa intenta identificar las columnas. Si es necesario, indique sus
nombres exactos:

```bash
python scripts/analiza_csv.py datos/crudos/vernier.csv \
  --time-column "Tiempo" --signal-column "Potencial" \
  --source Vernier --spacing-mm 40 \
  --output-dir resultados/equipo01
```

Para archivos con punto y coma y coma decimal:

```bash
python scripts/analiza_csv.py datos/crudos/vernier.csv \
  --sep ";" --decimal "," --source Vernier \
  --spacing-mm 40 --output-dir resultados/equipo01
```

## Estación B: sensor analógico y Arduino

La estación se realiza en tres fases y no debe conectarse al voluntario hasta
que el acoplador haya sido calculado y validado.

### B1. Diseño del acoplador

1. Consultar la hoja de datos del LM741 y documentar alimentación, terminales,
   excursión de salida y elementos externos recomendados.
2. Medir o establecer el intervalo esperado de la salida `SIG` del módulo.
3. Diseñar con dos LM741 una ganancia total positiva menor que uno, de modo que
   la salida permanezca dentro del intervalo del ADC.
4. Registrar resistencias, ganancia de cada etapa y ganancia total esperada.
 
### B2. Validación sin voluntario

1. Con el voluntario desconectado, probar inicialmente con una senoide de
   100 Hz y después en 20, 50, 100, 250 y 450 Hz.
2. Comparar entrada y salida con el osciloscopio y comprobar ganancia, offset,
   signo, saturación e intervalo máximo y mínimo.

El generador sólo se conecta a la entrada del acoplador, nunca a los electrodos
ni al voluntario. No se debe eliminar la tierra de protección del osciloscopio.

### B3. Adquisición con Arduino

1. Utilizar únicamente la interfaz aceptada por el docente.
2. Cargar `arduino/emg_arduino/emg_arduino.ino`.
3. Ajustar pin, referencia y resolución ADC al hardware real. La configuración
   inicial emplea 2000 muestras/s y 500000 baud.
4. Capturar y mostrar la señal desde Python:

```bash
python scripts/captura_arduino.py \
  --port COM3 --baud 500000 --seconds 30 --live-plot \
  --spacing-mm 20 --condition contraccion_carga_constante \
  --subject-code S01 \
  --output datos/crudos/arduino_d20.csv
```

5. El programa guarda `t_us`, tiempo, código ADC, voltaje, metadatos de
   regularidad temporal y una gráfica de la captura.
6. Analizar la columna de voltaje:

```bash
python scripts/analiza_csv.py datos/crudos/arduino_d20.csv \
  --time-column tiempo_s --signal-column voltaje_v \
  --source Arduino --condition contraccion_carga_constante \
  --spacing-mm 20 --subject-code S01 \
  --signal-unit V \
  --output-dir resultados/equipo01
```

El programa supone inicialmente un ADC de 10 bits y `Vref = 5 V`. Cambie
`--adc-bits` y `--vref` si utiliza otra tarjeta. Antes de interpretar la FFT o
la PSD, confirme que el módulo entrega EMG crudo. El espectro de una salida que
ya fue rectificada o suavizada no representa el espectro original del EMG.

## Estación C: PhysioNet

El programa descarga los archivos de texto oficiales de la base
`Examples of Electromyograms`, selecciona ventanas iguales y genera el mismo
conjunto de resultados:

```bash
python scripts/analiza_physionet.py \
  --start 0 --duration 2 \
  --output-dir resultados/equipo01/physionet
```

Para ocultar las condiciones en los nombres de salida:

```bash
python scripts/analiza_physionet.py --blind \
  --output-dir resultados/equipo01/physionet_ciego
```

Este modo sólo oculta la condición en los archivos generados; no es un cegado
estricto porque el código fuente y los nombres originales permiten identificar
los registros. Para una actividad realmente ciega, el docente deberá entregar
copias renombradas por separado.

Fuente de los registros: <https://physionet.org/content/emgdb/1.0.0/>.

## Procesamiento incluido

Para cada registro se conservan y calculan:

- señal cruda y señal centrada;
- filtrado pasa banda configurable;
- notch opcional, desactivado por defecto;
- rectificación de onda completa;
- envolvente de baja frecuencia;
- RMS móvil;
- RMS, MAV, iEMG y amplitud pico a pico;
- longitud de forma de onda y cruces por cero;
- PSD mediante Welch;
- potencia espectral de la señal integrada en la banda analizada;
- frecuencia media y frecuencia mediana.

RMS, envolvente y PSD cuantifican la actividad eléctrica registrada. No miden
directamente fuerza ni potencia mecánica. Para estudiar fuerza se necesita un
dinamómetro, una celda de carga o una carga externa controlada.

## Comparación de resultados

Después de analizar las señales:

```bash
python scripts/comparar_resultados.py resultados/equipo01 \
  --output-dir resultados/equipo01/comparacion
```

El script reúne todos los archivos `*_resumen.csv`, produce una tabla completa
y genera figuras separadas para cada fuente. Las amplitudes de Vernier,
Arduino y PhysioNet no deben compararse directamente porque pueden tener
unidades, ganancias, electrodos y bandas diferentes.

## Qué se publica en Git

Sí se publican:

- código y parámetros;
- códigos anónimos;
- separación de los electrodos y descripción del protocolo;
- ventanas seleccionadas;
- tablas de características;
- figuras derivadas;
- esquema, cálculos y validación del acoplador;
- informe y conclusiones.

No se publican:

- nombres, matrículas o datos identificables;
- archivos fisiológicos crudos de estudiantes;
- series temporales procesadas muestra por muestra;
- fotografías identificables de la colocación;
- credenciales o configuraciones privadas.

Consulte `docs/PUBLICACION_GIT.md` para crear el repositorio y subir la entrega.

## Seguridad y alcance

Este material tiene fines docentes y no constituye software médico. El
generador se utiliza sólo con el voluntario desconectado. Una adquisición en
personas requiere alimentación por baterías y el esquema de aislamiento
autorizado por el laboratorio. No se debe conectar directamente al voluntario
un osciloscopio referenciado a tierra ni una computadora alimentada desde la
red sin el aislamiento previsto por el responsable del laboratorio.

## Referencias principales

- Webster, J. G., y Nimunkar, A. J. (eds.). *Medical Instrumentation:
  Application and Design*, 5.a ed., Wiley, 2020.
- Husar, P., y Gašpar, G. *Electrical Biosignals in Biomedical Engineering*.
  Springer, 2023.
- PhysioNet. *Examples of Electromyograms*, versión 1.0.0.
- Vernier. *EKG Sensor User Manual*, EKG-BTA.

## Licencias

El código de este repositorio se distribuye con licencia MIT. Los datos de
PhysioNet conservan su propia licencia y atribución; el programa los descarga
desde su fuente oficial y no los redistribuye dentro de este ZIP.
