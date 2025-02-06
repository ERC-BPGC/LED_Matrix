#include <WiFi.h>
#include <WiFiUdp.h>
#include <Adafruit_NeoPixel.h>
#ifdef AVR
 #include <avr/power.h>
#endif

const char *ssid = "iPhone";
const char *password = "bakchodi";

WiFiUDP udp;
const unsigned int udpPort = 12345;
char incomingPacket[2047];

#define NUM_STRIPS 4
#define LEDS_PER_STRIP 40
#define FRAME_COMMANDS (NUM_STRIPS * LEDS_PER_STRIP)
const int STRIP_PINS[NUM_STRIPS] = {13,12,14,27};

Adafruit_NeoPixel strips[NUM_STRIPS] = {
    Adafruit_NeoPixel(LEDS_PER_STRIP, STRIP_PINS[0], NEO_GRB + NEO_KHZ800),
    Adafruit_NeoPixel(LEDS_PER_STRIP, STRIP_PINS[1], NEO_GRB + NEO_KHZ800),
    Adafruit_NeoPixel(LEDS_PER_STRIP, STRIP_PINS[2], NEO_GRB + NEO_KHZ800),
    Adafruit_NeoPixel(LEDS_PER_STRIP, STRIP_PINS[3], NEO_GRB + NEO_KHZ800)
};

TaskHandle_t WiFiMonitorTask;
TaskHandle_t NeoPixelTask;

volatile bool isWiFiConnected = false;

// Increased to support multiple commands
#define MAX_COMMANDS 1600
struct LEDCommand {
    int stripNum;
    int pixelNum;
    uint32_t color;
    bool isValid;
};

struct Frame {
    LEDCommand commands[FRAME_COMMANDS];
    int count;
};

volatile struct Frame *latestFrame = NULL;
portMUX_TYPE frameMux = portMUX_INITIALIZER_UNLOCKED;

LEDCommand commandQueue[MAX_COMMANDS];
volatile int commandQueueCount = 0;
volatile bool newCommandsAvailable = false;
volatile int head = 0;  // Points to the next write position
volatile int tail = 0;  // Points to the next read position
portMUX_TYPE queueMux = portMUX_INITIALIZER_UNLOCKED;

// Color code mapping
uint32_t colorCodes[256]; // Array to hold color mappings

void initializeColorCodes() {
    // Initialize the colorCodes array with default values
    colorCodes['r'] = Adafruit_NeoPixel::Color(255, 0, 0);    // Red
    colorCodes['g'] = Adafruit_NeoPixel::Color(0, 255, 0);    // Green
    colorCodes['b'] = Adafruit_NeoPixel::Color(0, 0, 255);    // Blue
    colorCodes['y'] = Adafruit_NeoPixel::Color(255, 255, 0);  // Yellow
    colorCodes['c'] = Adafruit_NeoPixel::Color(0, 255, 255);  // Cyan
    colorCodes['m'] = Adafruit_NeoPixel::Color(255, 0, 255);  // Magenta
    colorCodes['w'] = Adafruit_NeoPixel::Color(255, 255, 255);// White
    colorCodes['d'] = Adafruit_NeoPixel::Color(100, 100, 100);   // Dim Gray
    colorCodes['o'] = Adafruit_NeoPixel::Color(255, 165, 0);  // Orange
    colorCodes['v'] = Adafruit_NeoPixel::Color(127, 0, 255);  // Violet
    colorCodes['i'] = Adafruit_NeoPixel::Color(75, 0, 130);   // Indigo
}

// void parseCommands(const char* message) {
//     commandQueueCount = 0;
//     char* token = strtok((char*)message, "/");
    
//     while (token != NULL && commandQueueCount < MAX_COMMANDS) {
//         char *endPtr;
//         LEDCommand cmd = {0, 0, 0, false};
        
//         // Parse strip number
//         cmd.stripNum = strtol(token, &endPtr, 10);
//         if (endPtr == token || *endPtr != '.') break;
        
//         // Move past the dot
//         token = endPtr + 1;
        
//         // Parse pixel number
//         cmd.pixelNum = strtol(token, &endPtr, 10);
//         if (endPtr == token || *endPtr != '&') break;
        
//         // Parse color code
//         char colorCode = *(endPtr + 1);
//         cmd.color = colorCodes[colorCode];
        
//         // Validate ranges
//         if (cmd.stripNum >= 1 && cmd.stripNum <= NUM_STRIPS &&
//             cmd.pixelNum >= 1 && cmd.pixelNum <= LEDS_PER_STRIP) {
//             cmd.isValid = true;
//             portENTER_CRITICAL(&queueMux);
//             int nextHead = (head + 1) % MAX_COMMANDS;
//             if (nextHead != tail) { // Ensure buffer is not full
//                 commandQueue[head] = cmd;
//                 head = nextHead;
//             }
//             portEXIT_CRITICAL(&queueMux);
//             Serial.printf("Parsed Command %d:\n", commandQueueCount);
//             Serial.printf("Strip: %d\n", cmd.stripNum);
//             Serial.printf("Color: %d\n", colorCode);
//             Serial.printf("Pixel: %d\n", cmd.pixelNum);
//         }
        
//         // Get next token
//         token = strtok(NULL, "/");
//     }
    
//     if (commandQueueCount > 0) {
//         newCommandsAvailable = true;
//     }
// }
void parseCommands(const char* message) {
    // Allocate a new frame
    struct Frame* newFrame = (struct Frame*) malloc(sizeof(struct Frame));
    if (!newFrame) return;
    newFrame->count = 0;
    
    char* msgCopy = strdup(message); // make a modifiable copy
    char* token = strtok(msgCopy, "/");
    while (token != NULL && newFrame->count < FRAME_COMMANDS) {
        char *endPtr;
        LEDCommand cmd = {0, 0, 0, false};
        
        // Parse strip number
        cmd.stripNum = strtol(token, &endPtr, 10);
        if (endPtr == token || *endPtr != '.') break;
        token = endPtr + 1;
        
        // Parse pixel number
        cmd.pixelNum = strtol(token, &endPtr, 10);
        if (endPtr == token || *endPtr != '&') break;
        
        // Parse color code
        char colorCode = *(endPtr + 1);
        cmd.color = colorCodes[colorCode];
        
        // Validate ranges (strip 1-4, pixel 1-40)
        if (cmd.stripNum >= 1 && cmd.stripNum <= NUM_STRIPS &&
            cmd.pixelNum >= 1 && cmd.pixelNum <= LEDS_PER_STRIP) {
            cmd.isValid = true;
            newFrame->commands[newFrame->count++] = cmd;
        }
        
        token = strtok(NULL, "/");
    }
    free(msgCopy);
    
    // Only if we got a full frame do we accept it:
    if (newFrame->count == FRAME_COMMANDS) {
        portENTER_CRITICAL(&frameMux);
        if (latestFrame != NULL) {
            free((void*)latestFrame); // drop older frame(s)
        }
        latestFrame = newFrame;
        portEXIT_CRITICAL(&frameMux);
        Serial.println("DEBUG: Valid frame received (160 commands parsed).");
    } else {
        free(newFrame);
    }
}
void WiFiMonitorCode(void *parameter) {
    Serial.print("Connecting to WiFi");
    WiFi.begin(ssid, password);
    
    for(;;) {
        if (WiFi.status() == WL_CONNECTED) {
            if (!isWiFiConnected) {
                isWiFiConnected = true;
                Serial.println("\nConnected to WiFi");
                udp.begin(udpPort);
                Serial.printf("Listening on UDP port %d\n", udpPort);
                Serial.print("ESP32 IP address: ");
                Serial.println(WiFi.localIP());
            }
            
            int packetSize = udp.parsePacket();
            if (packetSize) {
                int len = udp.read(incomingPacket, sizeof(incomingPacket) - 1);
                if (len > 0) {
                    incomingPacket[len] = 0;
                    Serial.printf("Received command: %s\n", incomingPacket);
                    
                    parseCommands(incomingPacket);
                }
            }
        } else {
            if (isWiFiConnected) {
                isWiFiConnected = false;
                Serial.println("WiFi connection lost! Reconnecting...");
                WiFi.reconnect();
            }
            Serial.print(".");
            delay(500);
        }
        delay(10);
    }
}

// void NeoPixelCode(void *parameter) {
//     for(int i = 0; i < NUM_STRIPS; i++) {
//         strips[i].begin();
//         strips[i].show();
//         strips[i].setBrightness(150);
//     }

//     for(;;) {
//         portENTER_CRITICAL(&queueMux);
//         if (head != tail) {  // If there is a command to process
//             LEDCommand cmd = commandQueue[tail];
//             tail = (tail + 1) % MAX_COMMANDS;
//             portEXIT_CRITICAL(&queueMux);

//             if (cmd.isValid) {
//                 int stripIndex = cmd.stripNum - 1;
//                 int pixelIndex = cmd.pixelNum - 1;
//                 strips[stripIndex].setPixelColor(pixelIndex, cmd.color);
//                 strips[stripIndex].show();
//                 //dev uncle
//             }
//         } else {
//             portEXIT_CRITICAL(&queueMux);
//         }
//         delay(1); // Small delay to allow other tasks to run
//     }
// }
void NeoPixelCode(void *parameter) {
    // Initialize all strips.
    for(int i = 0; i < NUM_STRIPS; i++) {
        strips[i].begin();
        strips[i].show();
        strips[i].setBrightness(150);
    }

    for(;;) {
        // Check if a new frame is available.
        portENTER_CRITICAL(&frameMux);
        struct Frame *frameToProcess = (struct Frame*) latestFrame;
        latestFrame = NULL; // Remove the frame (drop any older frames)
        portEXIT_CRITICAL(&frameMux);
        
        if (frameToProcess != NULL) {
            // Process every command in the frame.
            // (You can choose to process commands one by one or all at once.)
            for (int i = 0; i < frameToProcess->count; i++) {
                LEDCommand cmd = frameToProcess->commands[i];
                if (cmd.isValid) {
                    int stripIndex = cmd.stripNum - 1;   // Convert to 0-indexed
                    int pixelIndex = cmd.pixelNum - 1;     // Convert to 0-indexed
                    strips[stripIndex].setPixelColor(pixelIndex, cmd.color);
                }
            }
            // Update all strips (you may call show() once for each strip).
            for (int i = 0; i < NUM_STRIPS; i++) {
                strips[i].show();
            }
            Serial.println("DEBUG: Frame processed on core 1 (NeoPixel task).");
            free(frameToProcess);
        }
        delay(1); // Yield a little before checking again.
    }
}

void setup() {
    Serial.begin(115200);
    
    // Initialize color codes
    initializeColorCodes();
    
    xTaskCreatePinnedToCore(
        WiFiMonitorCode,
        "WiFiMonitor",
        10000,
        NULL,
        1,
        &WiFiMonitorTask,
        0
    );
    
    xTaskCreatePinnedToCore(
        NeoPixelCode,
        "NeoPixel",
        10000,
        NULL,
        1,
        &NeoPixelTask,
        1
    );
}

void loop() {}
