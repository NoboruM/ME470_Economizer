#include "ADS1X15.h"
 
ADS1115 ADS(0x48);

#define R1 10000

float A = 0.001595266148;
float B = 0.0001480202732;
float C = 0.0000004882061793;
 
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
  
  Serial.print("Analog1: "); Serial.print(Vout_1, 3);  Serial.print("V\t"); Serial.print(ohms_1, 2); Serial.print("OHMs\t"); Serial.print(ohm_to_temp(ohms_1),2); Serial.println("C");
  Serial.print("Analog2: "); Serial.print(Vout_2, 3);  Serial.print("V\t"); Serial.print(ohms_2, 2); Serial.print("OHMs\t"); Serial.print(ohm_to_temp(ohms_2),2); Serial.println("C");
  Serial.print("Analog3: "); Serial.print(Vout_3, 3);  Serial.print("V\t"); Serial.print(ohms_3, 2); Serial.print("OHMs\t"); Serial.print(ohm_to_temp(ohms_3),2); Serial.println("C");
  Serial.println("");
  delay(1000);
}

float ohm_to_temp(float R)
{
  float T = 1/(A + (B*log(R)) + (C*(log(R)*log(R)*log(R))));

  float Tc = T - 273.15;

  return Tc;
}
