#include <Wire.h>
#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

#define SLAVE_ADDRESS 0
#define NEOPIXEL_PIN 4
#define NEOPIXEL_PIN2 5
#define ARRAY_SIZE 40

Adafruit_NeoPixel strip = Adafruit_NeoPixel(ARRAY_SIZE, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip2 = Adafruit_NeoPixel(ARRAY_SIZE, NEOPIXEL_PIN2, NEO_GRB + NEO_KHZ800);

void setup() {
  /*#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
  #endif
  */
  Wire.begin(SLAVE_ADDRESS);
  

  strip.begin();
  strip.show(); // Initialize NeoPixel strip
  strip.setBrightness(255);
}

int a = 0;

void loop() {
  Wire.onReceive(receiveEvent);
}

void receiveEvent(int numBytes) {

  String receivedString = "";
   // Loop through all received bytes
  
  if (Wire.available() > 0) 
  {
      
      receivedString = "";
      for(int j=0;j<7;j++)
      {
        char c = Wire.read(); // Read the received byte
        receivedString += c; // Append the character to the received string
      }
      Serial.println(receivedString);
      int red = strtol(receivedString.substring(1, 3).c_str(), NULL, 16);
      int green = strtol(receivedString.substring(3, 5).c_str(), NULL, 16);
      int blue = strtol(receivedString.substring(5, 7).c_str(), NULL, 16);
      Serial.println((String)red + " " + (String)green + " " +(String)blue + " " );
      if(a>=40)
        strip2.setPixelColor(a-40, strip.Color(red,blue,green));
      else
        strip.setPixelColor(a, strip.Color(red,blue,green));
      if(a == 80)
        a = 0;
      strip.show();
      a++;
  }
  
}