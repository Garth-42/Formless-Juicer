/*
  created 9 May 2011
  by Tom Igoe

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/SerialEvent
*/

String inputString = "";         // a String to hold incoming data
String lastString = "";
bool stringComplete = false;  // whether the string is complete

const int stepPin1 = 36; 
const int dirPin1 = 34;

const int stepPin2 = A6;
const int dirPin2 = A7;

const int stepPin3 = 46; 
const int dirPin3 = 48;

void setup() {
  // initialize serial:
  Serial.begin(9600);
  // reserve 200 bytes for the inputString:
  inputString.reserve(200);
  // Pump1 (E1 on RAMPS)
  pinMode(stepPin1,OUTPUT); 
  pinMode(dirPin1,OUTPUT);
  pinMode(30, OUTPUT); // Motor enable
  digitalWrite(30, LOW);
  // Pump2 (Y on RAMPS)
  pinMode(A6,OUTPUT); 
  pinMode(A7,OUTPUT);
  pinMode(A2, OUTPUT); // Motor enable
  digitalWrite(A2, LOW);
  // Pump3
  pinMode(stepPin3,OUTPUT); 
  pinMode(dirPin3,OUTPUT);
  pinMode(A8, OUTPUT); // Motor enable
  digitalWrite(A8, LOW);
}

void loop() {
  // print the string when a newline arrives:
  if (stringComplete) {
    Serial.println(inputString);
    
    // clear the string:
    lastString = inputString;
    inputString = "";
    stringComplete = false;
  }
  // If input matches this, turn pump 1
  if (lastString == "Turn1\n"){
    //Serial.println("turn!");
    digitalWrite(dirPin1,HIGH);
    digitalWrite(stepPin1,HIGH); 
    delayMicroseconds(500); 
    digitalWrite(stepPin1,LOW); 
    delayMicroseconds(500);
  }
  if (lastString == "Turn2\n"){
    //Serial.println("turn!");
    digitalWrite(dirPin2,HIGH);
    digitalWrite(stepPin2,HIGH); 
    delayMicroseconds(500); 
    digitalWrite(stepPin2,LOW); 
    delayMicroseconds(500);
  }
  if (lastString == "Turn3\n"){
    //Serial.println("turn!");
    digitalWrite(dirPin3,HIGH);
    digitalWrite(stepPin3,HIGH); 
    delayMicroseconds(500); 
    digitalWrite(stepPin3,LOW); 
    delayMicroseconds(500);
  }
}

/*
  SerialEvent occurs whenever a new data comes in the hardware serial RX. This
  routine is run between each time loop() runs, so using delay inside loop can
  delay response. Multiple bytes of data may be available.
*/
void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag so the main loop can
    // do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}
