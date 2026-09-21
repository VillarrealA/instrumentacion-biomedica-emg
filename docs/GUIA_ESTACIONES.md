# Guía de trabajo por estaciones

## Protocolo común

La variable experimental para Vernier y Arduino es la separación entre los
centros de los electrodos. Seleccionen tres separaciones físicamente posibles y
anoten las distancias reales. Si el tamaño del electrodo no permite usar la
separación propuesta, no superpongan los electrodos.

Mantengan constantes:

- músculo, sujeto y postura;
- punto medio entre los electrodos;
- orientación respecto a las fibras;
- posición del electrodo de referencia;
- carga o fuerza objetivo;
- duración de las ventanas;
- ganancia, filtros y frecuencia de muestreo dentro de cada equipo.

Conviene emplear una carga externa fija o un objetivo de fuerza medido. Las
indicaciones subjetivas como “leve” o “fuerte” producen comparaciones menos
controladas.

## Estación A: Vernier

1. Identifiquen el modelo y el canal utilizado.
2. Verifiquen si el software muestra potencial crudo, EMG rectificado u otra
   variable.
3. Marquen el punto medio del arreglo sobre el músculo.
4. Registren reposo y una contracción isométrica estable para cada separación.
5. Realicen al menos dos repeticiones.
6. Exporten tiempo y potencial a CSV.
7. Analicen intervalos de la misma duración.

## Estación B: módulo EMG, acoplador y Arduino

### Diseño del acoplador

1. Identifiquen en el módulo `+VS`, `GND`, `-VS`, `SIG` y la entrada de
   electrodos. No confundan el módulo EMG con el ADC del Arduino.
2. Consulten la hoja de datos del LM741 y registren terminales, alimentación,
   excursión de entrada y salida, ancho de banda y componentes externos
   recomendados por el fabricante.
3. Establezcan el intervalo esperado de `SIG` y el permitido por el ADC.
4. Con dos LM741, propongan una interfaz cuya ganancia total sea positiva y
   menor que uno. Calculen resistencias, ganancias parciales y ganancia total.
5. Si `SIG` contiene valores negativos, expliquen por qué la atenuación por sí
   sola no es suficiente y propongan el desplazamiento de nivel requerido.

### Validación sin voluntario

1. Desconecten completamente al voluntario y los electrodos.
2. Apliquen al acoplador una senoide inicial de 100 Hz. Aumenten la amplitud
   progresivamente hasta reproducir el intervalo esperado de `SIG`.
3. Repitan en 20, 50, 100, 250 y 450 Hz.
4. Con el canal 1 observen la entrada y con el canal 2 la salida.
5. Midan ganancia, offset, signo, valores mínimo y máximo y ausencia de recorte.
6. Comprueben que la salida se mantiene dentro del intervalo aceptado por el
   ADC. Conserven fotografías o capturas del osciloscopio.
7. Completen `resultados/plantilla_validacion_acoplador.csv`.

### Adquisición

1. Utilicen únicamente la interfaz aceptada por el docente.
2. Documenten resolución ADC, referencia, ganancia total y muestreo real.
3. Repitan el protocolo de separaciones de la estación Vernier.
4. Comprueben saturación, códigos utilizados, jitter y pérdidas de muestras.
5. Guarden el CSV únicamente en la carpeta local de datos crudos.

### Seguridad

- El generador se utiliza sólo con el voluntario desconectado.
- Con una persona conectada se empleará alimentación por baterías y el esquema
  de aislamiento autorizado por el laboratorio.
- No se conectará directamente un osciloscopio referenciado a tierra ni se
  eliminará su conexión de protección.

## Estación C: PhysioNet

Los registros son EMG de aguja adquirido en tibialis anterior y remuestreado a
4 kHz. No representan distintas separaciones interelectródicas.

1. Analicen los tres registros con ventanas de igual duración.
2. Comparen señal temporal, rectificación, envolvente, RMS y PSD.
3. Calculen frecuencia media, frecuencia mediana, cruces por cero y longitud de
   forma de onda.
4. Describan diferencias observables sin convertirlas en diagnóstico.

## Preguntas para la discusión

1. ¿Qué variables cambian de forma consistente con la separación?
2. ¿Una amplitud mayor implica necesariamente mayor activación muscular?
3. ¿Qué cambios pueden explicarse por crosstalk o cancelación espacial?
4. ¿Los resultados se repiten entre ensayos?
5. ¿Qué fracción del espectro puede conservar cada sistema?
6. ¿Existe una componente estrecha alrededor de 60 Hz?
7. ¿El acoplador presentó la ganancia prevista en toda la banda?
8. ¿El ADC utiliza adecuadamente su intervalo sin saturarse?
9. ¿Qué diferencias provienen del músculo, de la colocación y de la interfaz?

## Análisis opcionales

- relación entre RMS de contracción y RMS de reposo;
- coeficiente de variación entre repeticiones;
- potencia espectral de la señal alrededor de 60 Hz;
- tiempo de inicio estimado a partir de la envolvente;
- evolución de RMS y frecuencia mediana durante una contracción sostenida;
- normalización respecto a una contracción voluntaria máxima, si el protocolo
  y la supervisión permiten obtenerla de forma segura.

La fatiga sólo debe interpretarse cuando la fuerza y la postura se mantienen
aproximadamente constantes. Un descenso de la frecuencia mediana por sí solo no
demuestra fatiga en un protocolo no controlado.
