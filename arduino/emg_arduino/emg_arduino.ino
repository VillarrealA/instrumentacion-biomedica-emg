/*
  Adquisición genérica de un sensor EMG analógico.

  Salida serie: t_us,adc
  Configuración inicial: A0, 2000 muestras/s, 500000 baud.

  IMPORTANTE: úsen sólo con el montaje revisado por el profesor. Un sistema
  conectado a una persona requiere alimentación, aislamiento y protección
  adecuados. No conecten un montaje corporal no evaluado a una computadora
  alimentada desde la red.
*/

const uint8_t EMG_PIN = A0;
const uint32_t FS_HZ = 2000;
const uint32_t SAMPLE_PERIOD_US = 1000000UL / FS_HZ;
const uint32_t BAUD_RATE = 500000;

uint32_t siguienteMuestra = 0;

void setup() {
  Serial.begin(BAUD_RATE);

  // No se fija la referencia ni la resolución desde el programa. Tanto el
  // Mega 2560 como el UNO R4 WiFi inician en el modo compatible de 10 bits
  // empleado por captura_arduino.py. La entrada debe permanecer entre 0 y 5 V.
  delay(1000);
  Serial.println("t_us,adc");
  siguienteMuestra = micros();
}

void loop() {
  const uint32_t ahora = micros();
  if ((int32_t)(ahora - siguienteMuestra) >= 0) {
    siguienteMuestra += SAMPLE_PERIOD_US;
    const uint32_t instanteLectura = micros();
    const int muestra = analogRead(EMG_PIN);
    Serial.print(instanteLectura);
    Serial.print(',');
    Serial.println(muestra);

    // Evita una ráfaga de muestras si alguna transmisión se retrasa más de
    // un periodo completo. El archivo de captura conserva los tiempos reales.
    if ((int32_t)(micros() - siguienteMuestra) >= 0) {
      siguienteMuestra = micros() + SAMPLE_PERIOD_US;
    }
  }
}
