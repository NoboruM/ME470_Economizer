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
  int16_t val_0 = ADS.readADC(0);
  int16_t val_1 = ADS.readADC(1);
  int16_t val_2 = ADS.readADC(2);
  int16_t val_3 = ADS.readADC(3);  
  float f = ADS.toVoltage(1);  // voltage factor
  float Vin = val_0 * f;
  float Vout_1 = val_1 * f;
  float Vout_2 = val_2 * f;
  float Vout_3 = val_3 * f;
  float ohms_1 = R1*(Vin/Vout_1 - 1);
  float ohms_2 = R1*(Vin/Vout_2 - 1);
  float ohms_3 = R1*(Vin/Vout_3 - 1);
  
  Serial.print("Analog1: "); Serial.print(Vout_1, 3);  Serial.print("V\t"); Serial.print(ohms_1, 2); Serial.println("OHMs");
  Serial.print("Analog2: "); Serial.print(Vout_2, 3);  Serial.print("V\t"); Serial.print(ohms_2, 2); Serial.println("OHMs");
  Serial.print("Analog3: "); Serial.print(Vout_3, 3);  Serial.print("V\t"); Serial.print(ohms_3, 2); Serial.println("OHMs");
  Serial.println("");
  delay(1000);
}
