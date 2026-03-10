const int numButtons = 10;
const int buttonPins[numButtons] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11};

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < numButtons; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
  }
}

void loop() {
  for (int i = 0; i < numButtons; i++) {
    if (digitalRead(buttonPins[i]) == LOW) {
      Serial.println(i);  // Send the button index over serial
      delay(200); // Simple debounce delay
    }
  }
}