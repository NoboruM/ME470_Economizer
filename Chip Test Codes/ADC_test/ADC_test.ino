#include "ADS1X15.h"
 
ADS1115 ADS(0x48);

#define R1 10000
 
void setup() 
{
  Serial.begin(115200);
 
  ADS.begin();
}
 
 
void loop() 
{
  ADS.setGain(0);
 
  int16_t val_1 = ADS.readADC(1);  
  int16_t val_2 = ADS.readADC(2);  
  float f = ADS.toVoltage(1);  // voltage factor
  float Vin = val_2 * f;
  float Vout = val_1 * f;
  float ohms = R1*(Vin/Vout - 1);
 
  Serial.print("\tAnalog1: "); Serial.print(val_1); Serial.print('\t'); Serial.print(Vout, 3);  Serial.print("V\t"); Serial.print(ohms, 2); Serial.println("OHMs");
 
  delay(500);
}
