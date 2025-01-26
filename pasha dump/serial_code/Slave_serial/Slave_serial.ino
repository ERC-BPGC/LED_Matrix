#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

#define NEOPIXEL_PIN 4
#define NEOPIXEL_PIN2 5
#define ARRAY_SIZE 40
char id1 = '0';
char id2 = '0';

Adafruit_NeoPixel strip = Adafruit_NeoPixel(ARRAY_SIZE, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip2 = Adafruit_NeoPixel(ARRAY_SIZE, NEOPIXEL_PIN2, NEO_GRB + NEO_KHZ800);

void setup() {
  /*#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
  #endif
  */
  Serial.begin(115200);
  strip.begin();
  strip.show(); // Initialize NeoPixel strip
  strip.setBrightness(255);
}

String temp;
int no = 0;
bool st1 = 0;
int red = 0;
int green = 0;
int blue = 0;

void loop() {
  if (Serial.available() > 0) 
  {
    Serial.read(temp,7);
    if(temp[0] == '$')
      {
        if(temp[1] == id1 && temp[1] == id2)
        {
          st1 = 1;
        }
        else
        {
          st1 = 0;
        }
      }
    else if(temp[0] == '#')
    {
      String str = String(temp);
      red = strtol(str.substring(1, 3).c_str(), NULL, 16);
      green = strtol(str.substring(3, 5).c_str(), NULL, 16);
      blue = strtol(str.substring(5, 7).c_str(), NULL, 16);
    }
    else
    {
      red = 0;
      green = 0;
      blue = 0;
    }
    if(st1 == 1)
      strip.setPixelColor(no, strip.Color(red,blue,green));
    else
      strip2.setPixelColor(no, strip.Color(red,blue,green));
    
    if(no == 39)
      no = -1;
    no++;
  }
}
