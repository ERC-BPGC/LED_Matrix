#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(115200);
}

String inp = "";


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
            int a = j*7;
            arr[j][i] = (String)inp.substring(a,a+7);
            //sendArrayToSlave((int)i/2,(String)inp.substring(a,a+7));
        }
      }
      //send_it(inp);
    }
  }
}

void sendArrayToSlave(int slaveAddress, String item) {
  ///send_it(item);
  Wire.beginTransmission(slaveAddress);
  Wire.write((const uint8_t*)item.c_str(),item.length());
  Wire.endTransmission();
}