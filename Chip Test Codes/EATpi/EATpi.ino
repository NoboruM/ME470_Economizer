#include <SPI.h>
#include <SdFat.h>
#include "ADS1X15.h"
#include "RTClib.h"

SdFat SD;
ADS1115 ADS(0x48);
RTC_PCF8523 rtc;

#define DEBUG_MOTOR true

#define pin_CS 10
#define pin_DET 2
#define R1 10000

#define pin_LED_red 6
#define pin_LED_white 8

#define default_sample_rate 15
#define default_recording_state 0
#define default_last_sample_time 0
#define default_recording_file_name "tmp.csv"

float A = 0.001595266148;
float B = 0.0001480202732;
float C = 0.0000004882061793;

bool is_SD_in = false;

bool is_recording = false;
bool is_recording_light_on = false;
uint16_t sample_rate = default_sample_rate;
unsigned long last_sample_time = default_last_sample_time;
String recording_file_name = default_recording_file_name;

unsigned long last_recording_check = 0;
unsigned long curr_time = 0;

struct EAT_measurement
{
  unsigned long time_stamp;
  float OAT;
  float MAT;
  bool motor_state;
};

typedef struct EAT_measurement Measurement;

void setup() 
{
  Serial.begin(115200);
  ADS.begin();
  pinMode(pin_DET, INPUT);
  pinMode(pin_CS, OUTPUT);

  SD_init();
  
  while(!is_SD_in)
  {
    delay(5000);
    SD_init();
  }
  
  check_config();
  rtc.begin();
}

void loop() 
{
  //wait until a command can be read
  if(Serial.available() > 0)
  {
    parse_command();
  }

  if(is_recording)
  {
    if(millis() - last_recording_check > 500)
    {
      curr_time = rtc.now().unixtime();
      
      if(is_recording && (curr_time-last_sample_time > (sample_rate * 60-1) || curr_time-last_sample_time < 0))
      {
        if(!record_data())
        {
          Serial.println("DATA RECORDING ERROR!");
        }
      }
  
      last_recording_check = millis();

      if(is_recording_light_on)
      {
        is_recording_light_on = false;
        digitalWrite(pin_LED_red, LOW);
      }
      else
      {
        is_recording_light_on = true;
        digitalWrite(pin_LED_red, HIGH);
      }
  
      //maybe also add something in here to check if the SD card was taken out
    }
  }
      
#if DEBUG_MOTOR
  if(get_motor_state())
  {
    digitalWrite(pin_LED_white, HIGH);
  }
  else
  {
    digitalWrite(pin_LED_white, LOW);
  }
#endif
}

bool record_data()
{
  File _file = SD.open(recording_file_name, FILE_WRITE);

  //if there is no file give a parameter error
  if(!_file)
  {
    return false;
  }

  if(_file.size() < 4)
  {
    _file.println("Date,OAT,MAT,Motor State");
  }
  
  Measurement _data = measure();

  _file.println(String(_data.time_stamp)+","+f2str(_data.OAT)+","+f2str(_data.MAT)+","+_data.motor_state);

  _file.close();

  if(cmd_s_lst(curr_time))
  {
    last_sample_time = curr_time;
  }
  else
  {
    return false;
  }

  return true;
}

Measurement measure()
{
  Measurement _data_out;
  
  int16_t _val_0 = ADS.readADC(0);
  int16_t _val_1 = ADS.readADC(1);
  int16_t _val_3 = ADS.readADC(3);  
  float _f = ADS.toVoltage(1);  // voltage factor
  float _Vin = _val_0 * _f;
  float _Vout_1 = _val_1 * _f;
  float _Vout_3 = _val_3 * _f;
  float _ohms_1 = R1*(_Vin/_Vout_1 - 1);
  float _ohms_3 = R1*(_Vin/_Vout_3 - 1);
  
  _data_out.time_stamp = rtc.now().unixtime();
  _data_out.OAT = ohm_to_temp(_ohms_3);
  _data_out.MAT = ohm_to_temp(_ohms_1);
  _data_out.motor_state = get_motor_state();

  return _data_out;
}

float ohm_to_temp(float _R)
{
  float _T = 1/(A + (B*log(_R)) + (C*(log(_R)*log(_R)*log(_R))));
  float _Tc = _T - 273.15;
  float _Tf = (_Tc * 1.8) + 32;

  return _Tf;
}

bool get_motor_state()
{
  int16_t _last_measurement = 0;
  int16_t _curr_measurement = ADS.readADC(2);
  unsigned long _sum = 0;
  
  for (int i = 0; i<25; i++)
  {
    _sum += abs(_curr_measurement-_last_measurement);
    _last_measurement = _curr_measurement;
    _curr_measurement = ADS.readADC(2);
    delay(10);
  }
  float _ans = _sum/25;
  
  if(_ans > 150)
  {
    return true;
  }
  
  return false;
}

void SD_init()
{
  if (!SD.begin(pin_CS))
  {
    is_SD_in = false;
  }
  else
  {
    is_SD_in = true;
  }
  return;
}

//convert float to string
String f2str(float _data)
{
  return String(float(round(_data * 10)) / 10.0).substring(0,4);
}
