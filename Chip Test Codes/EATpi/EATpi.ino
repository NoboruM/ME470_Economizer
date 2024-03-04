#include <SPI.h>
#include <SdFat.h>
#include "ADS1X15.h"

SdFat SD;
File myFile;
ADS1115 ADS(0x48);

#define pin_CS 10
#define pin_DET 2
#define R1 10000

bool is_SD_in = false;

void setup() 
{
  Serial.begin(115200);
  ADS.begin();
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
  myFile = SD.open("Test File.csv", FILE_WRITE);
  if(myFile)
  {
    myFile.println("Date, Arduino Time, ADC Reading, Voltage, Resistance");
    myFile.flush();
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

  if(is_SD_in)
  {
    measure();
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

short measure()
{
  int16_t _val_1 = ADS.readADC(1);  
  int16_t _val_2 = ADS.readADC(2);  
  float _f = ADS.toVoltage(1);  // voltage factor
  float _Vin = _val_2 * _f;
  float _Vout = _val_1 * _f;
  float _ohms = R1*(_Vin/_Vout - 1);
  Serial.println("Today," + String(millis()) + "ms," + String(_val_1) +","+ String(_Vout)+"V,"+ String(_ohms)+"OHMS");
  short _e = myFile.println("Today," + String(millis()) + "ms," + String(_val_1) +","+ String(_Vout)+"V,"+ String(_ohms)+"OHMS");
  myFile.flush();

  return _e;
}
