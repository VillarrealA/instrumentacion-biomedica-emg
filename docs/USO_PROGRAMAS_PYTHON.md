# Guía de uso de los programas de Python

Esta guía describe el flujo completo para adquirir, procesar y comparar las
señales de la práctica de electromiografía. Todos los comandos deben ejecutarse
desde la carpeta principal del repositorio:

```text
instrumentacion-biomedica-emg/
```

Los programas ya están preparados. El trabajo del equipo consiste en registrar
correctamente las condiciones experimentales, seleccionar intervalos
comparables e interpretar los resultados.

## 1. Preparación inicial

### 1.1 Abrir una terminal en la carpeta correcta

En el Explorador de archivos de Windows, abra la carpeta
`instrumentacion-biomedica-emg`. Después escriba `powershell` en la barra de
direcciones y presione Enter.

Compruebe la ubicación con:

```powershell
Get-Location
```

En esa carpeta deben verse `README.md`, `requirements.txt`, `scripts/`,
`arduino/` y `docs/`.

### 1.2 Comprobar Python

```powershell
python --version
```

Si Windows no reconoce `python`, pruebe:

```powershell
py --version
```

En ese caso puede sustituir `python` por `py` en todos los comandos de esta
guía.

### 1.3 Instalar las dependencias

Opción sencilla:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Opción recomendada con un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si PowerShell impide activar el entorno, habilítelo únicamente para la terminal
actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Cuando el entorno está activo aparece `(.venv)` al inicio de la línea.

## 2. Programas disponibles

| Programa | Función | Se ejecuta directamente |
|---|---|---|
| `scripts/ejecutar_demo.py` | Comprueba la instalación con señales sintéticas | Sí |
| `scripts/captura_arduino.py` | Recibe `t_us,adc` por el puerto serie | Sí |
| `scripts/analiza_csv.py` | Procesa CSV de Vernier, Arduino u otra fuente | Sí |
| `scripts/analiza_physionet.py` | Descarga y procesa tres registros de PhysioNet | Sí |
| `scripts/comparar_resultados.py` | Integra archivos `*_resumen.csv` | Sí |
| `scripts/generar_datos_demo.py` | Regenera los datos sintéticos de demostración | Sólo si se solicita |
| `scripts/emg_core.py` | Contiene las funciones utilizadas por los demás programas | No |

Para consultar las opciones de cualquier programa utilice `--help`. Por
ejemplo:

```powershell
python scripts/analiza_csv.py --help
```

## 3. Comprobación antes de la práctica

Ejecute:

```powershell
python scripts/ejecutar_demo.py
```

El programa debe terminar con el mensaje:

```text
Demostración terminada. Revise resultados/demo/.
```

Si la demostración funciona, Python, NumPy, SciPy, pandas y Matplotlib están
disponibles y el procesamiento básico puede ejecutarse.

## 4. Estación A: Vernier

### 4.1 Exportar el registro

Desde Graphical Analysis o Logger Pro, exporte las columnas de tiempo y señal a
CSV. Guarde el archivo dentro de `datos/crudos/`, por ejemplo:

```text
datos/crudos/vernier_d20.csv
```

No use nombres de estudiantes. La separación indicada en el nombre es la
distancia centro a centro entre los electrodos.

### 4.2 Identificar columnas y unidades

Abra el CSV con un editor de texto o una hoja de cálculo e identifique:

- nombre de la columna de tiempo;
- nombre de la columna de señal;
- unidad del tiempo;
- unidad de la señal;
- separador de columnas: coma o punto y coma;
- separador decimal: punto o coma.

El programa intenta reconocer las columnas automáticamente. Una ejecución
básica sería:

```powershell
python scripts/analiza_csv.py datos/crudos/vernier_d20.csv --source Vernier --condition contraccion_carga_constante --spacing-mm 20 --subject-code S01 --signal-unit mV --output-dir resultados/equipo01/vernier
```

Si no reconoce las columnas, indique sus nombres exactamente como aparecen en
el archivo:

```powershell
python scripts/analiza_csv.py datos/crudos/vernier_d20.csv --time-column "Tiempo" --signal-column "Potencial" --source Vernier --condition contraccion_carga_constante --spacing-mm 20 --subject-code S01 --signal-unit mV --output-dir resultados/equipo01/vernier
```

Para un CSV con punto y coma y coma decimal agregue:

```text
--sep ";" --decimal ","
```

### 4.3 Seleccionar el intervalo

Para analizar, por ejemplo, desde 5 hasta 15 segundos:

```text
--start 5 --end 15
```

Utilice intervalos de la misma duración para comparar las tres separaciones.

### 4.4 Repetir el análisis

Repita el procedimiento para `d1`, `d2` y `d3`, manteniendo constantes el
músculo, la postura, la carga, el punto medio de los electrodos y la duración de
la ventana.

## 5. Estación B: sensor analógico y Arduino

### 5.1 Preparar Arduino

1. Abra `arduino/emg_arduino/emg_arduino.ino` en Arduino IDE.
2. Seleccione la tarjeta y el puerto correctos.
3. Cargue el programa.
4. Cierre el Monitor serie y el Serial Plotter antes de ejecutar Python.

El mismo archivo es compatible con Mega 2560 y UNO R4 WiFi. La configuración
utilizada en la práctica es:

| Parámetro | Valor |
|---|---:|
| Entrada | `A0` |
| Frecuencia nominal | 2000 muestras/s |
| Periodo nominal | 500 microsegundos |
| Resolución utilizada | 10 bits |
| Intervalo de códigos | 0–1023 |
| Velocidad serie | 500000 baud |
| Formato transmitido | `t_us,adc` |

La señal aplicada a `A0` debe permanecer entre 0 y 5 V. La interfaz debe
validarse con generador y osciloscopio, sin voluntario, antes de conectarla al
ADC.

### 5.2 Identificar el puerto

El puerto puede consultarse en Arduino IDE, en `Herramientas > Puerto`. En
Windows tendrá una forma como `COM3`, `COM5` o `COM8`.

### 5.3 Capturar la señal

Ejemplo para una separación de 20 mm:

```powershell
python scripts/captura_arduino.py --port COM3 --baud 500000 --seconds 30 --adc-bits 10 --vref 5.0 --spacing-mm 20 --condition contraccion_carga_constante --subject-code S01 --output datos/crudos/arduino_d20.csv
```

Sustituya `COM3` por el puerto real. Si se midió una referencia diferente de
5.0 V, escriba el valor medido, por ejemplo `--vref 4.92`.

Para mostrar los últimos segundos mientras se adquiere, agregue:

```text
--live-plot
```

La visualización es opcional. Si la computadora pierde muestras al actualizar
la gráfica, realice la captura final sin `--live-plot`.

### 5.4 Archivos producidos por la captura

Para `arduino_d20.csv` se generan:

```text
datos/crudos/arduino_d20.csv
datos/crudos/arduino_d20.json
datos/crudos/arduino_d20_captura.png
```

El CSV contiene:

| Columna | Significado |
|---|---|
| `t_us` | Marca de tiempo transmitida por Arduino en microsegundos |
| `tiempo_s` | Tiempo relativo en segundos |
| `adc` | Código del convertidor A/D |
| `voltaje_v` | Voltaje calculado con la resolución y referencia indicadas |

El JSON registra frecuencia estimada, periodo mediano, jitter, muestras
perdidas, códigos mínimo y máximo y muestras cercanas a los rieles.

### 5.5 Analizar el CSV capturado

```powershell
python scripts/analiza_csv.py datos/crudos/arduino_d20.csv --time-column tiempo_s --signal-column voltaje_v --source Arduino --condition contraccion_carga_constante --spacing-mm 20 --subject-code S01 --signal-unit V --output-dir resultados/equipo01/arduino
```

Repita la captura y el análisis para las tres separaciones. Use nombres
diferentes para no sobrescribir archivos.

## 6. Estación C: PhysioNet

Para descargar y analizar los tres registros:

```powershell
python scripts/analiza_physionet.py --start 0 --duration 2 --output-dir resultados/equipo01/physionet
```

La primera ejecución requiere conexión a Internet. Los archivos descargados se
guardan localmente en `datos/physionet/` y no se publican en Git.

Para ocultar la condición en los nombres de los resultados:

```powershell
python scripts/analiza_physionet.py --blind --start 0 --duration 2 --output-dir resultados/equipo01/physionet_ciego
```

El modo `--blind` cambia las etiquetas de salida, pero no constituye un cegado
estricto porque las condiciones todavía pueden identificarse revisando el
código o los nombres de los archivos descargados.

## 7. Resultados generados por el análisis

`analiza_csv.py` y `analiza_physionet.py` producen, para cada señal:

| Archivo | Contenido |
|---|---|
| `*_analisis.png` | Señal cruda, filtrada, rectificada, envolvente, RMS y PSD |
| `*_metricas.json` | Metadatos, parámetros y métricas |
| `*_resumen.csv` | Una fila con los resultados principales |
| `*_psd.csv` | Frecuencia y densidad espectral de potencia |
| `*_procesada.csv` | Series temporales procesadas muestra por muestra |

Las variables principales incluyen RMS, MAV, iEMG, amplitud pico a pico,
frecuencia media, frecuencia mediana y potencia espectral integrada en la banda.
Estas variables describen la actividad eléctrica registrada; no son mediciones
directas de fuerza ni de potencia mecánica.

## 8. Comparación final

Cuando todos los resultados estén dentro de `resultados/equipo01/`, ejecute:

```powershell
python scripts/comparar_resultados.py resultados/equipo01 --output-dir resultados/equipo01/comparacion
```

El programa busca recursivamente todos los archivos `*_resumen.csv` y genera:

```text
comparacion_completa.csv
comparacion_Vernier.png
comparacion_Arduino.png
comparacion_PhysioNet_emgdb_1.0.0.png
```

Las amplitudes sólo deben compararse directamente dentro del mismo sistema y
con unidades consistentes. Vernier, Arduino y PhysioNet pueden tener electrodos,
ganancias, unidades y bandas diferentes.

## 9. Qué se conserva en Git

Sí se conservan:

- código y parámetros utilizados;
- esquema, cálculos y validación de la interfaz;
- archivos `*_resumen.csv`;
- archivos `*_metricas.json`;
- PSD y figuras seleccionadas;
- informe y conclusiones.

No se publican:

- nombres, matrículas u otros identificadores;
- archivos fisiológicos crudos de estudiantes;
- fotografías identificables;
- series procesadas muestra por muestra de participantes;
- credenciales o configuraciones privadas.

Antes de realizar el commit, compruebe:

```powershell
git status
```

## 10. Problemas frecuentes

### `python` no se reconoce

Pruebe `py` en lugar de `python`. Si tampoco funciona, instale Python y marque
la opción para agregarlo a `PATH`.

### `ModuleNotFoundError`

Active el entorno e instale las dependencias:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### `No module named serial`

```powershell
python -m pip install pyserial
```

### El puerto COM está ocupado o se niega el acceso

Cierre el Monitor serie, Serial Plotter y cualquier programa que esté usando el
puerto. Desconecte y vuelva a conectar Arduino si es necesario.

### Se recibieron muy pocas muestras

Compruebe:

- puerto correcto;
- `500000` baud tanto en Arduino como en Python;
- programa cargado y tarjeta reiniciada;
- cable USB con transmisión de datos;
- ausencia de otro programa conectado al puerto.

### Python no identifica las columnas del CSV

Use `--time-column` y `--signal-column` con los nombres exactos. Revise también
`--sep` y `--decimal`.

### La frecuencia de corte supera Nyquist

La frecuencia pasa bajas debe ser menor que `fs/2`. Para una señal muestreada a
500 Hz, por ejemplo, utilice una frecuencia de corte menor que 250 Hz:

```text
--lowpass 200
```

### Aparecen códigos cercanos a 0 o 1023

La interfaz puede estar saturando o utilizando inadecuadamente el intervalo del
ADC. Revise amplitud, offset, alimentación y conexiones antes de interpretar la
señal.

### Se reportan muestras perdidas

Repita sin `--live-plot`, cierre otros programas y verifique el cable USB. El
archivo JSON conserva la estimación para documentar la calidad de la captura.

## 11. Seguridad

La prueba con generador y osciloscopio se realiza con el voluntario
completamente desconectado. La adquisición en una persona sólo puede realizarse
con el esquema de alimentación y aislamiento autorizado por el laboratorio.
Nunca elimine la tierra de protección de un osciloscopio para intentar hacerlo
flotante.
