#define BUZZER_PIN 8

void beep(int times, int duration) {
  for (int i = 0; i < times; i++) {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(duration);
    digitalWrite(BUZZER_PIN, LOW);
    delay(duration);
  }
}

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  beep(2, 150);  // บี๊บ บี๊บ
  delay(2000);
}
