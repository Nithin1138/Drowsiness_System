// ============================================================
//  ECS Car System – LED & Pin Identifier Tool
//  Upload this sketch to test every Arduino digital pin from 2 to 13.
//  Open the Arduino Serial Monitor (9600 baud) to watch which Pin is
//  currently HIGH and verify which LED lights up!
// ============================================================

void setup() {
  Serial.begin(9600);
  Serial.println("ECS Pin Identifier Tool Ready!");
  Serial.println("Setting all pins 2 to 13 to OUTPUT and LOW...");
  
  for (int pin = 2; pin <= 19; pin++) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
  }
  
  delay(1000);
}

void loop() {
  for (int pin = 2; pin <= 19; pin++) {
    // Report current pin to Serial Monitor
    Serial.print("PIN ");
    Serial.print(pin);
    if (pin >= 14) {
      Serial.print(" (A");
      Serial.print(pin - 14);
      Serial.print(")");
    }
    Serial.println(" is now HIGH (LED should glow)");

    // Turn pin HIGH
    digitalWrite(pin, HIGH);
    delay(2500); // Hold for 2.5 seconds to allow observation
    
    // Turn pin LOW
    digitalWrite(pin, LOW);
    delay(500);  // Brief gap before next pin
  }
  
  Serial.println("=========================================");
  Serial.println("Cycle completed. Restarting in 3 seconds...");
  Serial.println("=========================================");
  delay(3000);
}
