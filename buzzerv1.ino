#define BUZZER_PIN 8

void setup() {
}

void loop() {
  tone(BUZZER_PIN, 1000); // 1000 Hz
  delay(300);
  noTone(BUZZER_PIN);
  delay(700);
}
