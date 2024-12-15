#define LPIN 11

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
 #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif
#define LED_PIN    5
#define LED_COUNT 40

Adafruit_NeoPixel strip(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);


void setup() {

  Serial.begin(115200);

  pinMode(LPIN, OUTPUT);
  digitalWrite(LPIN, LOW);

  #if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
  #endif
  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
}

uint8_t l = 0;

String inp;
String arr[40][20];


void send_it(String s)
{
  for (int i = 0; i < s.length(); i++)
  {
    Serial.write(s[i]);   // Push each char 1 by 1 on each loop pass

  }

}

void loop() {
  if (Serial.available() > 0) {
    for(int i = 0; i<20; i++)
    {
      inp = Serial.readString;
      for(int j = 0; j < 40; j++)
      {
        int a = j*7;
        arr[j][i] = (String)inp.substring(a,a+7);
      }
    }
    /*
    for(int i = 0; i < 40; i++)
    {
      int red = strtol(first[i].substring(1, 3).c_str(), NULL, 16);
      int green = strtol(first[i].substring(3, 5).c_str(), NULL, 16);
      int blue = strtol(first[i].substring(5, 7).c_str(), NULL, 16);
      strip.setPixelColor(i, strip.Color(red,blue,green));
      strip.show();
    }
    */
  }
}

