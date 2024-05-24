/*
  Serial Event example

  When new serial data arrives, this sketch adds it to a String.
  When a newline is received, the loop prints the string and clears it.

  A good test for this is to try it with a GPS receiver that sends out
  NMEA 0183 sentences.

  NOTE: The serialEvent() feature is not available on the Leonardo, Micro, or
  other ATmega32U4 based boards.

  created 9 May 2011
  by Tom Igoe

  This example code is in the public domain.

  http://www.arduino.cc/en/Tutorial/SerialEvent
*/

#define PIN_OUT1 2
#define PIN_OUT2 3
#define PIN_OUT3 4
#define PIN_OUT4 5
#define PIN_OUT5 6
#define PIN_OUT6 7

#define PIN_IN1 8
#define PIN_IN2 9
#define PIN_IN3 10
#define PIN_IN4 11
#define PIN_IN5 12
#define PIN_IN6 13

int InputState1 = 0;
int InputState2 = 0;
int InputState3 = 0;
int InputState4 = 0;
int InputState5 = 0;
int InputState6 = 0;

// Variables will change:
int buttonPushCounter1 = 0;   // counter for the number of button presses
int lastButtonState1 = 0;     // previous state of the button 1

String inputString = "";         // a String to hold incoming data
bool stringComplete = false;  // whether the string is complete

void setup() {
  // initialize serial:
  Serial.begin(115200);
  // reserve 200 bytes for the inputString:
  inputString.reserve(200);

  pinMode(PIN_OUT1, OUTPUT);
  pinMode(PIN_OUT2, OUTPUT);
  pinMode(PIN_OUT3, OUTPUT);
  pinMode(PIN_OUT4, OUTPUT);
  pinMode(PIN_OUT5, OUTPUT);
  pinMode(PIN_OUT6, OUTPUT);

  pinMode(PIN_IN1, INPUT);
  pinMode(PIN_IN2, INPUT);
  pinMode(PIN_IN3, INPUT);
  pinMode(PIN_IN4, INPUT);
  pinMode(PIN_IN5, INPUT);
  pinMode(PIN_IN6, INPUT);

}

void loop() {
  // print the string when a newline arrives:
  if (stringComplete) {

    //=======================================//
    //Output 1
    if(inputString.equals("OUT1=1\n"))
    {
        digitalWrite(PIN_OUT1, HIGH); 
    }
    else if(inputString.equals("OUT1=0\n"))
    {
        digitalWrite(PIN_OUT1, LOW); 
    }

    //=======================================//
    //Output 2
    if(inputString.equals("OUT2=1\n"))
    {
        digitalWrite(PIN_OUT2, HIGH); 
    }
    else if(inputString.equals("OUT2=0\n"))
    {
        digitalWrite(PIN_OUT2, LOW); 
    }

    //=======================================//
    //Output 3
    if(inputString.equals("OUT3=1\n"))
    {
        digitalWrite(PIN_OUT3, HIGH); 
    }
    else if(inputString.equals("OUT3=0\n"))
    {
        digitalWrite(PIN_OUT3, LOW); 
    }

    //=======================================//
    //Output 4
    if(inputString.equals("OUT4=1\n"))
    {
        digitalWrite(PIN_OUT4, HIGH); 
    }
    else if(inputString.equals("OUT4=0\n"))
    {
        digitalWrite(PIN_OUT4, LOW); 
    }

    //=======================================//
    //Output 5
    if(inputString.equals("OUT5=1\n"))
    {
        digitalWrite(PIN_OUT5, HIGH); 
    }
    else if(inputString.equals("OUT5=0\n"))
    {
        digitalWrite(PIN_OUT5, LOW); 
    }

    //=======================================//
    //Output 6
    if(inputString.equals("OUT6=1\n"))
    {
        digitalWrite(PIN_OUT6, HIGH); 
    }
    else if(inputString.equals("OUT6=0\n"))
    {
        digitalWrite(PIN_OUT6, LOW); 
    }
    
    Serial.println(inputString);
    // clear the string:
    inputString = "";
    stringComplete = false;
  }

   //=======================================//
   //=======================================//
   // Input
   InputState1 = digitalRead(PIN_IN1);
   InputState2 = digitalRead(PIN_IN2);
   InputState3 = digitalRead(PIN_IN3);
   InputState4 = digitalRead(PIN_IN4);
   InputState5 = digitalRead(PIN_IN5);
   InputState6 = digitalRead(PIN_IN6);

   // compare the buttonState to its previous state
  if (InputState1 != lastButtonState1) {
    // if the state has changed, increment the counter
    if (InputState1 == HIGH) {
      // if the current state is HIGH then the button went from off to on:
      buttonPushCounter1++;
      Serial.println("IN1=1");
      Serial.print("NUM=");
      Serial.println(buttonPushCounter1);

      if(buttonPushCounter1 >= 99){
        buttonPushCounter1 = 0;
      }
    } else {
      // if the current state is LOW then the button went from on to off:
      Serial.println("IN1=0");
    }
    // Delay a little bit to avoid bouncing
    delay(50);
  }
  // save the current state as the last state, for next time through the loop
  lastButtonState1 = InputState1;
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
