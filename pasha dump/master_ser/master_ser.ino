void setup() {
  Serial.begin(115200);
}

String inp = "";

void loop() {
  if (Serial.available() > 0) 
  {
    
    for(int i = 0; i<20; i++)
    {
      inp = Serial.readStringUntil('\n');
      if (inp != "")
      {
        if(i<10)
        {
          Serial.println("$0"+(String)i + "0000");
        }
        else
        {
          Serial.println("$"+(String)i + "0000");
        }
        for(int j = 0; j < 40; j++)
        {
            int a = j*7;
            Serial.println((String)inp.substring(a,a+7));
        }
      }
    }
  }
}