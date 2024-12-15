// A basic everyday NeoPixel strip test program.

// NEOPIXEL BEST PRACTICES for most reliable operation:
// - Add 1000 uF CAPACITOR between NeoPixel strip's + and - connections.
// - MINIMIZE WIRING LENGTH between microcontroller board and first pixel.
// - NeoPixel strip's DATA-IN should pass through a 300-500 OHM RESISTOR.
// - AVOID connecting NeoPixels on a LIVE CIRCUIT. If you must, ALWAYS
//   connect GROUND (-) first, then +, then data.
// - When using a 3.3V microcontroller with a 5V-powered NeoPixel strip,
//   a LOGIC-LEVEL CONVERTER on the data line is STRONGLY RECOMMENDED.
// (Skipping these may work OK on your workbench but can fail in the field)

#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
 #include <avr/power.h> // Required for 16 MHz Adafruit Trinket
#endif

// Which pin on the Arduino is connected to the NeoPixels?
// On a Trinket or Gemma we suggest changing this to 1:
#define LED_PIN  2

// How many NeoPixels are attached to the Arduino?
#define LED_COUNT 40

// Declare our NeoPixel strip object:
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
  // These lines are specifically to support the Adafruit Trinket 5V 16 MHz.
  // Any other board, you can remove this part (but no harm leaving it):
#if defined(__AVR_ATtiny85__) && (F_CPU == 16000000)
  clock_prescale_set(clock_div_1);
#endif
  // END of Trinket-specific code.

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
  Serial.begin(115200);
}


// loop() function -- runs repeatedly as long as board is on ---------------

void loop() {
  // Fill along the length of the strip in various colors...
  
  //colorWipe(strip.Color(255,   0,   0), 50); // Red
  //colorWipe(strip.Color(  0, 255,   0), 5); // Blue
  //colorWipe(strip.Color(  0,   0, 255), 50); // Green

  // Do a theater marquee effect in various colors...
  //theaterChase(strip.Color(255, 255, 255), 50); // White, half brightness
  //theaterChase(strip.Color(255,   0,   0), 50); // Red, half brightness
  //theaterChase(strip.Color(  0,   0, 127), 50); // Blue, half brightness

  rainbow(1);             // Flowing rainbow cycle along the whole strip
  //theaterChaseRainbow(50); // Rainbow-enhanced theaterChase variant
  //india();
  //rando(100);
  //colorchoose(strip.Color(255,0,0));
  
  }

void rando_fade(int wait)
{
  colorchoose(strip.Color(random(0, 256),random(0, 256),random(0, 256)));
  delay(wait);
}

void rando(int wait)
{
  colorchoose(strip.Color(random(0, 256),random(0, 256),random(0, 256)));
  delay(wait);
}

// Some functions of our own for creating animated effects -----------------

// Fill strip pixels one after another with a color. Strip is NOT cleared
// first; anything there will be covered pixel by pixel. Pass in color
// (as a single 'packed' 32-bit value, which you can get by calling
// strip.Color(red, green, blue) as shown in the loop() function above),
// and a delay time (in milliseconds) between pixels.

void colorchoose(uint32_t color) {
  for(int i=0; i<180; i++) { // For each pixel in strip...
    strip.setPixelColor(i, color);         //  Set pixel's color (in RAM)
                             //  Update strip to match
                   //  Pause for a moment
  }
  strip.show(); 
}

void india() {
  for(int i=0; i<strip.numPixels()/3; i++) { // For each pixel in strip...
    strip.setPixelColor(i, strip.Color(255,5,40));         //  Set pixel's color (in RAM)
    strip.show();                          //  Update strip to match
                       //  Pause for a moment
  }
  
  for(int i=strip.numPixels()/3+1; i<2*strip.numPixels()/3; i++) { // For each pixel in strip...
    if(i != strip.numPixels()/2){
    strip.setPixelColor(i, strip.Color(150,150,150));         //  Set pixel's color (in RAM)
    strip.show();                          //  Update strip to match
    }                 //  Pause for a moment
  }
  for(int i=2*strip.numPixels()/3+1; i<strip.numPixels(); i++) { // For each pixel in strip...
    strip.setPixelColor(i, strip.Color(0,0,255));         //  Set pixel's color (in RAM)
    strip.show();                          //  Update strip to match
                    //  Pause for a moment
  }
  strip.setPixelColor(strip.numPixels()/2, strip.Color(0,255,0));
  strip.show();  
}

void colorWipe(uint32_t color, int wait) {
  for(int i=0; i<strip.numPixels(); i++) { // For each pixel in strip...
    strip.setPixelColor(i, color);         //  Set pixel's color (in RAM)
    strip.show();                          //  Update strip to match
    delay(wait);                           //  Pause for a moment
  }
}

// Theater-marquee-style chasing lights. Pass in a color (32-bit value,
// a la strip.Color(r,g,b) as mentioned above), and a delay time (in ms)
// between frames.
void theaterChase(uint32_t color, int wait) {
  for(int a=0; a<10; a++) {  // Repeat 10 times...
    for(int b=0; b<3; b++) { //  'b' counts from 0 to 2...
      strip.clear();         //   Set all pixels in RAM to 0 (off)
      // 'c' counts up from 'b' to end of strip in steps of 3...
      for(int c=b; c<strip.numPixels(); c += 3) {
        strip.setPixelColor(c, color); // Set pixel 'c' to value 'color'
      }
      strip.show(); // Update strip with new contents
      delay(wait);  // Pause for a moment
    }
  }
}

// Rainbow cycle along whole strip. Pass delay time (in ms) between frames.
void rainbow(int wait) {
  // Hue of first pixel runs 5 complete loops through the color wheel.
  // Color wheel has a range of 65536 but it's OK if we roll over, so
  // just count from 0 to 5*65536. Adding 256 to firstPixelHue each time
  // means we'll make 5*65536/256 = 1280 passes through this loop:
  for(long firstPixelHue = 0; firstPixelHue < 5*65536; firstPixelHue += 256) {
    // strip.rainbow() can take a single argument (first pixel hue) or
    // optionally a few extras: number of rainbow repetitions (default 1),
    // saturation and value (brightness) (both 0-255, similar to the
    // ColorHSV() function, default 255), and a true/false flag for whether
    // to apply gamma correction to provide 'truer' colors (default true).
    strip.rainbow(firstPixelHue);
    strip.show(); // Update strip with new contents
    strip2.rainbow(firstPixelHue);
    strip2.show(); // Update strip with new contents
    strip3.rainbow(firstPixelHue);
    strip3.show(); // Update strip with new contents
    strip4.rainbow(firstPixelHue);
    strip4.show(); // Update strip with new contents
    strip5.rainbow(firstPixelHue);
    strip5.show(); // Update strip with new contents
    strip6.rainbow(firstPixelHue);
    strip6.show(); // Update strip with new contents
    strip7.rainbow(firstPixelHue);
    strip7.show(); // Update strip with new contents
    strip8.rainbow(firstPixelHue);
    strip8.show(); // Update strip with new contents
    strip9.rainbow(firstPixelHue);
    strip9.show(); // Update strip with new contents
    strip10.rainbow(firstPixelHue);
    strip10.show(); // Update strip with new contents
    strip11.rainbow(firstPixelHue);
    strip11.show(); // Update strip with new contents
    strip12.rainbow(firstPixelHue);
    strip12.show(); // Update strip with new contents
    strip13.rainbow(firstPixelHue);
    strip13.show(); // Update strip with new contents
    strip14.rainbow(firstPixelHue);
    strip14.show(); // Update strip with new contents
    strip15.rainbow(firstPixelHue);
    strip15.show(); // Update strip with new contents
    strip16.rainbow(firstPixelHue);
    strip16.show(); // Update strip with new contents
    strip17.rainbow(firstPixelHue);
    strip17.show(); // Update strip with new contents
    strip18.rainbow(firstPixelHue);
    strip18.show(); // Update strip with new contents
    strip19.rainbow(firstPixelHue);
    strip19.show(); // Update strip with new contents
    strip20.rainbow(firstPixelHue);
    strip20.show(); // Update strip with new contents
    delay(wait);  // Pause for a moment
  }
}

// Rainbow-enhanced theater marquee. Pass delay time (in ms) between frames.
void theaterChaseRainbow(int wait) {
  int firstPixelHue = 0;     // First pixel starts at red (hue 0)
  for(int a=0; a<30; a++) {  // Repeat 30 times...
    for(int b=0; b<3; b++) { //  'b' counts from 0 to 2...
      strip.clear();         //   Set all pixels in RAM to 0 (off)
      // 'c' counts up from 'b' to end of strip in increments of 3...
      for(int c=b; c<strip.numPixels(); c += 3) {
        // hue of pixel 'c' is offset by an amount to make one full
        // revolution of the color wheel (range 65536) along the length
        // of the strip (strip.numPixels() steps):
        int      hue   = firstPixelHue + c * 65536L / strip.numPixels();
        uint32_t color = strip.gamma32(strip.ColorHSV(hue)); // hue -> RGB
        strip.setPixelColor(c, color); // Set pixel 'c' to value 'color'
      }
      strip.show();                // Update strip with new contents
      delay(wait);                 // Pause for a moment
      firstPixelHue += 65536 / 90; // One cycle of color wheel over 90 frames
    }
  }
}
