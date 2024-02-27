#include <SPI.h>
#include <SdFat.h>

SdFat SD;
File myFile;

#define pin_CS 10
#define pin_DET 2

bool is_SD_in = false;

void setup() 
{
  Serial.begin(9600);
  pinMode(pin_DET, INPUT);
  pinMode(pin_CS, OUTPUT);
  
  while (!Serial)
  {
    delay(1000);
  }
  
  SD_init();

  delay(1000);
  //make a file and write to it
  Serial.print("Creating an SD card file... ");
  myFile = SD.open("Test File.txt", FILE_WRITE);
  if(myFile)
  {
    myFile.println("Hello World!");
    myFile.close();
    Serial.println("Success.");
  }
  else
  {
    Serial.println("Failure.");
  }
  
}

void loop() {
  // put your main code here, to run repeatedly:
  if(digitalRead(pin_DET) && !is_SD_in)
  {
    SD_init();
  }
  else if (!digitalRead(pin_DET) && is_SD_in)
  {
    is_SD_in = false;
  }
  
  delay(5000);
}

void SD_init()
{
  Serial.print("Initializing SD card... ");
  if (!SD.begin(pin_CS))
  {
    Serial.println("SD Initialization fail");
    is_SD_in = false;
  }
  else
  {
    Serial.println("SD Initialization Success");
    is_SD_in = true;
  }
  return;
}
