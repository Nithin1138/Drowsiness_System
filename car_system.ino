// ============================================================
//  ECS Car System – Arduino Uno (Software Fallback Edition)
//  States received via Serial: N, Y, B, X, E
//  Note: Since the physical Green LED is broken/disconnected, 
//        we use the working Blue/Yellow LED & Red LED for all indications.
// ============================================================

// -------- Motor driver pins (L298N) --------
const int motor1_in1 = 2;
const int motor1_in2 = 3;
const int motor2_in3 = 4;
const int motor2_in4 = 5;
const int ENA        = 9;   // PWM for Motor A
const int ENB        = 10;  // PWM for Motor B

// -------- Other components --------
const int buzzer     = 8;
const int led_yellow = 12;  // used as "blue" indicator (our main status light)
const int led_red    = 13;  // used as "sleepy/emergency" status light

// -------- State management --------
char currentState     = 'N';   // start in Normal
char previousState    = ' ';
bool stateJustChanged = true;

// -------- Timing helpers --------
unsigned long stateEntryTime   = 0;   // millis() when we entered current state
unsigned long lastBuzzerToggle = 0;
unsigned long buzzerStartTime  = 0;
int  buzzerBeepCount           = 0;
bool buzzerOn                  = false;
bool bBeepsDone                = false;

// -------- Motor speed --------
const int FULL_SPEED = 200;   // 0-255 PWM
int  currentSpeed    = FULL_SPEED;

// ============================================================
//  LOW-LEVEL HELPERS
// ============================================================

void allLEDsOff() {
  digitalWrite(led_yellow, LOW);
  digitalWrite(led_red,    LOW);
}

void buzzerOff() {
  digitalWrite(buzzer, LOW);
  buzzerOn = false;
}

// Drive both motors forward at the given PWM speed
void motorsForward(int speed) {
  speed = constrain(speed, 0, 255);
  digitalWrite(motor1_in1, HIGH);
  digitalWrite(motor1_in2, LOW);
  digitalWrite(motor2_in3, HIGH);
  digitalWrite(motor2_in4, LOW);
  analogWrite(ENA, speed);
  analogWrite(ENB, speed);
}

// Stop both motors immediately
void motorsStop() {
  digitalWrite(motor1_in1, LOW);
  digitalWrite(motor1_in2, LOW);
  digitalWrite(motor2_in3, LOW);
  digitalWrite(motor2_in4, LOW);
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}

// ============================================================
//  STATE HANDLERS
// ============================================================

// ---------- N : Awake -> Blue LED solid ON, wheels moving ----------
void handleState_N() {
  if (stateJustChanged) {
    allLEDsOff();
    buzzerOff();
    digitalWrite(led_yellow, HIGH); // Solid Blue for normal state
    currentSpeed = FULL_SPEED;
    stateJustChanged = false;
  }
  motorsForward(currentSpeed);
}

// ---------- Y : Yawning -> Blue LED flashing slow, wheels moving ----------
void handleState_Y() {
  if (stateJustChanged) {
    allLEDsOff();
    buzzerOff();
    currentSpeed = FULL_SPEED;
    stateJustChanged = false;
  }
  
  // Flash Blue/Yellow LED slow: 500ms ON, 500ms OFF
  if ((millis() / 500) % 2 == 0) {
    digitalWrite(led_yellow, HIGH);
  } else {
    digitalWrite(led_yellow, LOW);
  }
  
  motorsForward(currentSpeed);
}

// ---------- B : Drowsy -> Blue LED flashing fast, buzzer 2×, wheels running ----------
void handleState_B() {
  if (stateJustChanged) {
    allLEDsOff();
    buzzerOff();
    currentSpeed    = FULL_SPEED;
    buzzerBeepCount = 0;
    bBeepsDone      = false;
    buzzerOn        = false;
    buzzerStartTime = millis();
    lastBuzzerToggle = millis();
    stateJustChanged = false;
  }

  // --- Two short beeps (200 ms ON, 200 ms OFF each) ---
  if (!bBeepsDone) {
    unsigned long now = millis();
    if (!buzzerOn && (now - lastBuzzerToggle >= 200)) {
      // start a beep
      digitalWrite(buzzer, HIGH);
      buzzerOn = true;
      lastBuzzerToggle = now;
    }
    if (buzzerOn && (now - lastBuzzerToggle >= 200)) {
      // end a beep
      digitalWrite(buzzer, LOW);
      buzzerOn = false;
      lastBuzzerToggle = now;
      buzzerBeepCount++;
      if (buzzerBeepCount >= 2) {
        bBeepsDone = true;
        buzzerOff();
      }
    }
  }

  // Flash Blue/Yellow LED fast: 150ms ON, 150ms OFF
  if ((millis() / 150) % 2 == 0) {
    digitalWrite(led_yellow, HIGH);
  } else {
    digitalWrite(led_yellow, LOW);
  }

  motorsForward(currentSpeed);
}

// ---------- X : Sleepy -> Red light ON constantly, wheels moving, buzzer ON ----------
void handleState_X() {
  if (stateJustChanged) {
    allLEDsOff();
    digitalWrite(led_red, HIGH);  // Solid Red
    digitalWrite(buzzer, HIGH);   // continuous buzzer
    buzzerOn     = true;
    currentSpeed = FULL_SPEED;
    stateJustChanged = false;
  }
  motorsForward(currentSpeed);
}

// ---------- E : Emergency -> Red light ON constantly, continuous buzzer, slow stop after 5 s ----------
void handleState_E() {
  if (stateJustChanged) {
    allLEDsOff();
    digitalWrite(led_red, HIGH);  // Solid Red
    digitalWrite(buzzer, HIGH);   // continuous buzzer
    buzzerOn     = true;
    currentSpeed = FULL_SPEED;
    stateJustChanged = false;
  }

  // Gradually reduce speed after 5 seconds in this state
  unsigned long elapsed = millis() - stateEntryTime;

  if (elapsed > 5000) {
    // Linear ramp-down over the next 3 seconds (5 s -> 8 s)
    unsigned long rampElapsed = elapsed - 5000;
    if (rampElapsed >= 3000) {
      currentSpeed = 0;           // fully stopped
    } else {
      currentSpeed = FULL_SPEED - (int)((long)FULL_SPEED * rampElapsed / 3000);
    }
  }

  if (currentSpeed > 0) {
    motorsForward(currentSpeed);
  } else {
    motorsStop();
  }
}

// ============================================================
//  SETUP
// ============================================================
void setup() {
  Serial.begin(9600);

  // Motor pins
  pinMode(motor1_in1, OUTPUT);
  pinMode(motor1_in2, OUTPUT);
  pinMode(motor2_in3, OUTPUT);
  pinMode(motor2_in4, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(ENB, OUTPUT);

  // Indicators
  pinMode(buzzer,     OUTPUT);
  pinMode(led_yellow, OUTPUT);
  pinMode(led_red,    OUTPUT);

  // Start in state N
  allLEDsOff();
  buzzerOff();
  motorsStop();

  currentState     = 'N';
  stateJustChanged = true;
  stateEntryTime   = millis();

  Serial.println("ECS Car System Ready  |  Send: N / Y / B / X / E");
}

// ============================================================
//  MAIN LOOP
// ============================================================
void loop() {

  // ---- Read incoming state from Serial ----
  if (Serial.available() > 0) {
    char incoming = Serial.read();

    // Accept only valid state characters
    if (incoming == 'N' || incoming == 'Y' || incoming == 'B' ||
        incoming == 'X' || incoming == 'E') {

      if (incoming != currentState) {
        previousState    = currentState;
        currentState     = incoming;
        stateJustChanged = true;
        stateEntryTime   = millis();

        Serial.print("State -> ");
        Serial.println(currentState);
      }
    }
  }

  // ---- Dispatch to current state handler ----
  switch (currentState) {
    case 'N': handleState_N(); break;
    case 'Y': handleState_Y(); break;
    case 'B': handleState_B(); break;
    case 'X': handleState_X(); break;
    case 'E': handleState_E(); break;
    default:  handleState_N(); break;   // fallback
  }

  delay(10);   // small debounce / loop pacing
}
