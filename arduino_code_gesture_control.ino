int ledPins[] = {8, 9, 10};

void setup() {
  for (int i = 0; i < 3; i++) pinMode(ledPins[i], OUTPUT);
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char gesture = Serial.read();
    switch (gesture) {
      case '1': runChaser(); break;
      case '2': allFlash(); break;
      case '3': centerOut(); break;
      case '4': sparkle(); break;
    }
  }
}

void runChaser() {
  for (int i = 0; i < 3; i++) {
    digitalWrite(ledPins[i], HIGH);
    delay(200);
    digitalWrite(ledPins[i], LOW);
  }
}

void allFlash() {
  for (int j = 0; j < 3; j++) {
    digitalWrite(ledPins[j], HIGH);
  }
  delay(200);
  for (int j = 0; j < 3; j++) {
    digitalWrite(ledPins[j], LOW);
  }
  delay(200);
}

void centerOut() {
  digitalWrite(ledPins[1], HIGH); delay(150);
  digitalWrite(ledPins[0], HIGH); delay(150);
  digitalWrite(ledPins[2], HIGH); delay(150);
  for (int i = 0; i < 3; i++) digitalWrite(ledPins[i], LOW);
}

void sparkle() {
  for (int i = 0; i < 10; i++) {
    int r = random(0, 3);
    digitalWrite(ledPins[r], HIGH);
    delay(100);
    digitalWrite(ledPins[r], LOW);
  }
}