#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif



//#define NEOPIXEL_PIN[20] = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]
#define LED_COUNT 40

Adafruit_NeoPixel strip(LED_COUNT, 15, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip2(LED_COUNT, 2, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip3(LED_COUNT, 0, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip4(LED_COUNT, 4, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip5(LED_COUNT, 16, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip6(LED_COUNT, 17, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip7(LED_COUNT, 5, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip8(LED_COUNT, 18, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip9(LED_COUNT, 19, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip10(LED_COUNT, 21, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip11(LED_COUNT, 22, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip12(LED_COUNT, 23, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip13(LED_COUNT, 13, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip14(LED_COUNT, 12, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip15(LED_COUNT, 14, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip16(LED_COUNT, 27, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip17(LED_COUNT, 26, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip18(LED_COUNT, 25, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip19(LED_COUNT, 33, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip20(LED_COUNT, 32, NEO_GRB + NEO_KHZ800);

void setup() {
  strip.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip.show();            // Turn OFF all pixels ASAP
  strip.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip2.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip2.show();            // Turn OFF all pixels ASAP
  strip2.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip3.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip3.show();            // Turn OFF all pixels ASAP
  strip3.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip4.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip4.show();            // Turn OFF all pixels ASAP
  strip4.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip5.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip5.show();            // Turn OFF all pixels ASAP
  strip5.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip6.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip6.show();            // Turn OFF all pixels ASAP
  strip6.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip7.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip7.show();            // Turn OFF all pixels ASAP
  strip7.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip8.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip8.show();            // Turn OFF all pixels ASAP
  strip8.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip9.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip9.show();            // Turn OFF all pixels ASAP
  strip9.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip10.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip10.show();            // Turn OFF all pixels ASAP
  strip10.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip11.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip11.show();            // Turn OFF all pixels ASAP
  strip11.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip12.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip12.show();            // Turn OFF all pixels ASAP
  strip12.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip13.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip13.show();            // Turn OFF all pixels ASAP
  strip13.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip14.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip14.show();            // Turn OFF all pixels ASAP
  strip14.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip15.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip15.show();            // Turn OFF all pixels ASAP
  strip15.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip16.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip16.show();            // Turn OFF all pixels ASAP
  strip16.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip17.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip17.show();            // Turn OFF all pixels ASAP
  strip17.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip18.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip18.show();            // Turn OFF all pixels ASAP
  strip18.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip19.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip19.show();            // Turn OFF all pixels ASAP
  strip19.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  strip20.begin();           // INITIALIZE NeoPixel strip object (REQUIRED)
  strip20.show();            // Turn OFF all pixels ASAP
  strip20.setBrightness(255); // Set BRIGHTNESS to about 1/5 (max = 255)
  
  Serial.begin(4800);
}

String inp = "";
char temp;
String arr[103] = {"#021ed4", "#397b44", "#75D9A0", "#FA7036", "#0ea3e8", "#b6d53c", "#cfc6b8", "#4acc3b", "#f002e8", "#f5f5f5", "#78d7ff", "#d4514a", "#f47e1b", "#f1b5cb", "#0cb5f2", "#3dff6e", "#0444ba", "#7b1ff2", "#6e0202", "#FFE300", "#f777aa", "#ffaeb6", "#005285", "#401102", "#386641", "#e28df7", "#00ff00", "#9effae", "#f5f75e", "#0af7ef", "#f4b41b", "#f59905", "#ba5604", "#E8E8E8", "#ff3b05", "#28ccdf", "#bc4749", "#a93b3b", "#eb6f02", "#FFA500", "#d13408", "#D17FD6", "#032057", "#e6482e", "#16db93", "#ebbea8", "#92fc65", "#f0c297", "#ff0505", "#d4a50b", "#631111", "#81b29a", "#930ddb", "#9b6a6c", "#ffffff", "#367beb", "#39314b", "#3978a8", "#205907", "#bc3ff2", "#8e478c", "#c6d831", "#444444", "#583bcc", "#1a466b", "#302c2e", "#bd1411", "#f5a15d", "#f2022a", "#a7c957", "#dddddd", "#eb9e34", "#0e0f2c", "#ffff00", "#0eff0a", "#222222", "#fa753c", "#bd8111", "#013220", "#EB2226", "#050101", "#394778", "#6a994e", "#e2a0ff", "#ff8a05", "#852300", "#e94f37", "#ff0000", "#3f3cfa", "#4ddb0f", "#71aa34", "#7a0000", "#f4f1de", "#000000", "#a32603", "#db2525", "#080cd1", "#028000", "#bf0fb6", "#eea160", "#034d04", "#69DFDB", "#7d7071"};
void send_it(String s)
{
  for (int i = 0; i < s.length(); i++)
  {
    Serial.write(s[i]);   // Push each char 1 by 1 on each loop pass
  }
}

void loop() {
  if (Serial.available() > 0) 
  {
    for(int i = 0; i<20; i++)
    {
      inp = Serial.readStringUntil('\n');
      if (inp != "")
      {
        for(int j = 0; j < 40; j++)
        {
            //int a = j*7;
            //inp.substring(j,j+2).toCharArray(temp,1);
            temp = inp[j];
            //send_it(temp);
            int red = strtol(arr[(int)temp - 1].substring(1, 3).c_str(), NULL, 16);
            int green = strtol(arr[(int)temp - 1].substring(3, 5).c_str(), NULL, 16);
            int blue = strtol(arr[(int)temp - 1].substring(5, 7).c_str(), NULL, 16);
            
            switch(i)
            {
            case 19:
            {
              strip.setPixelColor(j, strip.Color(red,blue,green));
              strip.show();
              break;
            }
            
            case 18:
            {
              strip2.setPixelColor(j, strip2.Color(red,blue,green));
              strip2.show();
              break;
            }
            case 17:
            {
              strip3.setPixelColor(j, strip3.Color(red,blue,green));
              strip3.show();
              break;
            }
            case 16:
            {
              strip4.setPixelColor(j, strip4.Color(red,blue,green));
              strip4.show();
              break;
            }
            case 15:
            {
              strip5.setPixelColor(j, strip5.Color(red,blue,green));
              strip5.show();
              break;
            }
            case 14:
            {
              strip6.setPixelColor(j, strip6.Color(red,blue,green));
              strip6.show();
              break;
            }
            case 13:
            {
              strip7.setPixelColor(j, strip7.Color(red,blue,green));
              strip7.show();
              break;
            }
            case 12:
            {
              strip8.setPixelColor(j, strip8.Color(red,blue,green));
              strip8.show();
              break;
            }
            case 11:
            {
              strip9.setPixelColor(j, strip9.Color(red,blue,green));
              strip9.show();
              break;
            }
            case 10:
            {
              strip10.setPixelColor(j, strip10.Color(red,blue,green));
              strip10.show();
              break;
            }
            case 9:
            {
              strip11.setPixelColor(j, strip11.Color(red,blue,green));
              strip11.show();
              break;
            }
            case 8:
            {
              strip12.setPixelColor(j, strip12.Color(red,blue,green));
              strip12.show();
              break;
            }
            case 7:
            {
              strip13.setPixelColor(j, strip13.Color(red,blue,green));
              strip13.show();
              break;
            }
            case 6:
            {
              strip14.setPixelColor(j, strip14.Color(red,blue,green));
              strip14.show();
              break;
            }
            case 5:
            {
              strip15.setPixelColor(j, strip15.Color(red,blue,green));
              strip15.show();
              break;
            }
            case 4:
            {
              strip16.setPixelColor(j, strip16.Color(red,blue,green));
              strip16.show();
              break;
            }
            case 3:
            {
              strip17.setPixelColor(j, strip17.Color(red,blue,green));
              strip17.show();
              break;
            }

            case 2:
            {
              strip18.setPixelColor(j, strip18.Color(red,blue,green));
              strip18.show();
              break;
            }
            case 1:
            {
              strip19.setPixelColor(j, strip19.Color(red,blue,green));
              strip19.show();
              break;
            }
            case 0:
            {
              strip20.setPixelColor(j, strip20.Color(red,blue,green));
              strip20.show();
              break;
            }
            }
        }
      }
    }
  }
}
