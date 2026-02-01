// Use this code 
#define BUZZER_PIN 8

const int SETS = 5;
const int GAP_BETWEEN_SETS_MS = 2000;
const unsigned long REST_5_MIN_MS = 5UL * 60UL * 1000UL;

void beep() {  // บี๊บ 2 ครั้ง
  for (int i = 0; i < 2; i++) {
    digitalWrite(BUZZER_PIN, HIGH);  delay(150);
    digitalWrite(BUZZER_PIN, LOW);   delay(150);
  }
}

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {

  // ดัง 5 ชุด
  for (int set = 1; set <= SETS; set++) {
    beep();
    delay(GAP_BETWEEN_SETS_MS);
  }

  // พัก 5 นาที แล้ววนกลับไปดังใหม่
  delay(REST_5_MIN_MS);
}
