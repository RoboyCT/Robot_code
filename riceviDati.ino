char lettera;

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);  // LED integrato
  Serial.begin(9600);
  Serial1.begin(9600);
}

void loop() {
  if (Serial.available()) {
    lettera = Serial.read();

    Serial1.write(lettera);
  }
}
