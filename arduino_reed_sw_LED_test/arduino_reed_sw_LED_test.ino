#include <FastLED.h>

#define NUM_LEDS 3
const int LED_data = 12;  // the number of the pushbutton pin
const int buttonPin = 8;  // the number of the pushbutton pin
int buttonState = 0;  // variable for reading the pushbutton status
CRGB leds[3];

void setup() {
  // initialize the pushbutton pin as an input:
  FastLED.addLeds<WS2812, LED_data, GRB>(leds, NUM_LEDS);
  pinMode(buttonPin, INPUT);
  Serial.begin(9600);
}

void loop() {
  // read the state of the pushbutton value:
  buttonState = digitalRead(buttonPin);

  // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
  if (buttonState == HIGH) {
    leds[0] = CRGB(255, 0, 0);
    leds[1] = CRGB(0, 255, 0);
    leds[2] = CRGB(255, 0, 0);
    Serial.println("High");
  } else {
    leds[0] = CRGB(0, 0, 0);
    leds[1] = CRGB(0, 0, 0);
    leds[2] = CRGB(0, 0, 0);
    Serial.println("Low");
  }
  FastLED.show();
  delay(500);
}

