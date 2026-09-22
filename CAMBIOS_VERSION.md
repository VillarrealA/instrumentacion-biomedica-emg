# Cambios incluidos en esta versión

Esta versión reúne en un solo paquete todos los ajustes realizados para la
práctica de electromiografía.

## Documentación

- README principal reorganizado con el mismo estilo general de la práctica de
  ECG: objetivo, flujo de trabajo, documentación, estructura, instalación,
  estaciones, privacidad, seguridad y control de versiones.
- Nueva guía `docs/USO_PROGRAMAS_PYTHON.md` con instrucciones completas para
  instalar, probar y ejecutar todos los programas.
- Se conservan `docs/GUIA_ESTACIONES.md` y `docs/PUBLICACION_GIT.md`.

## Estación B

- El README sólo especifica las funciones que debe cumplir la interfaz:
  amplitud, polaridad, offset, ancho de banda, protección, alimentación y
  compatibilidad con el ADC.
- No se revela el número de amplificadores operacionales ni una topología de
  solución; el circuito debe ser deducido y justificado por los estudiantes.
- El programa `emg_arduino.ino` ya no utiliza `analogReference(DEFAULT)` ni
  `analogReadResolution()`, de modo que el mismo archivo puede emplearse con
  Mega 2560 y UNO R4 WiFi en el modo compatible de 10 bits.

## Programas incluidos

- captura serie desde Arduino a 2000 muestras/s;
- análisis de CSV de Vernier o Arduino;
- descarga y análisis de los registros EMG de PhysioNet;
- cálculo de señal filtrada, rectificación, envolvente, RMS, MAV, iEMG,
  FFT/PSD, potencia espectral y frecuencias media y mediana;
- comparación automática de archivos `*_resumen.csv`;
- datos sintéticos y resultados de demostración;
- prueba automática del núcleo de procesamiento.

## Privacidad y entrega

- Los registros fisiológicos crudos de estudiantes permanecen excluidos de
  Git mediante `.gitignore`.
- Se incluyen plantillas de metadatos, resultados, validación e informe.
- La entrega conserva código, parámetros, resultados derivados, figuras y
  conclusiones, sin identificadores personales.
