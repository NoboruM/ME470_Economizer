#include "ADS1X15.h"
 
ADS1115 ADS(0x48);

#define R1 10000
 
void setup() 
{
  Serial.begin(115200);

  //while(1) {Serial.println("Test!"); delay(1000);}
 
  ADS.begin();
  ADS.setGain(0);
}
 
 
void loop() 
{
  int16_t val_3 = ADS.readADC(3);
  int16_t val_0 = ADS.readADC(0);  
  float f = ADS.toVoltage(1);  // voltage factor
  float Vin = val_0 * f;
  float Vout = val_3 * f;
  float ohms = R1*(Vin/Vout - 1);
 
  Serial.print("Analog4: "); Serial.print(val_3); Serial.print('\t'); Serial.print(Vout, 3);  Serial.print("V\t"); Serial.print(ohms, 2); Serial.println("OHMs");
  delay(1000);
}
