#include <Wire.h>

#define ARRAY_SIZE 40
#define SLAVE_ADDRESS 8

// Define three arrays of RGB values
uint32_t colorsList1[ARRAY_SIZE];
uint32_t colorsList2[ARRAY_SIZE];
uint32_t colorsList3[ARRAY_SIZE];

// Initialize index and brightness
int currentListIndex = 0;
uint8_t brightness = 255; // Maximum brightness

void setup() {
  Wire.begin();
  Serial.begin(460800);

  // Initialize three lists of RGB values
  generateColorsListRGB(colorsList1, ARRAY_SIZE, 255, 0, 0); // Red, Blue, Green
  generateColorsListRGB(colorsList2, ARRAY_SIZE, 0, 255, 0); // Green, Red, Blue
  generateColorsListRGB(colorsList3, ARRAY_SIZE, 0, 0, 255); // Blue, Green, Red
}

void loop() {
  // Send the current list of RGB values to the slave
  switch (currentListIndex) {
    case 0:
      sendArrayToSlave(SLAVE_ADDRESS, colorsList1, ARRAY_SIZE, brightness);
      break;
    case 1:
      sendArrayToSlave(SLAVE_ADDRESS, colorsList2, ARRAY_SIZE, brightness);
      break;
    case 2:
      sendArrayToSlave(SLAVE_ADDRESS, colorsList3, ARRAY_SIZE, brightness);
      break;
  }

  // Switch to the next list for the next iteration
  currentListIndex = (currentListIndex + 1) % 3;

  delay(33); // Adjust delay as needed
}

void sendArrayToSlave(int slaveAddress, uint32_t* colorsToSend, int arraySize, uint8_t brightness) {
  Wire.beginTransmission(slaveAddress);

  // Send brightness value as the first byte
  Wire.write(brightness);

  for (int i = 0; i < arraySize; ++i) {
    Wire.write((uint8_t)((colorsToSend[i] >> 16) & 0xFF));  // Red
    Wire.write((uint8_t)((colorsToSend[i] >> 8) & 0xFF));   // Green
    Wire.write((uint8_t)(colorsToSend[i] & 0xFF));          // Blue
  }

  Wire.endTransmission();

  Serial.print("Sent array to slave at address ");
  Serial.println(slaveAddress);
}

