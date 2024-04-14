#include <SPI.h>
#include <SdFat.h>
#include "ADS1X15.h"
#include "RTClib.h"

SdFat SD;
ADS1115 ADS(0x48);
RTC_PCF8523 rtc;

#define pin_CS 10
#define pin_DET 2
#define R1 10000

#define default_sample_rate "15"
#define default_recording_state "0"
#define default_last_sample_time "0"
#define default_recording_file_name "tmp.csv"

float A = 0.001595266148;
float B = 0.0001480202732;
float C = 0.0000004882061793;

bool is_SD_in = false;

bool is_recording = false;
uint16_t sample_rate = default_sample_rate;
unsigned long last_sample_time = default_last_sample_time;
String recording_file_name = default_recording_file_name;

unsigned long last_recording_check = 0;
long curr_time = 0;

struct EAT_measurement
{
  long time_stamp;
  float OAT;
  float MAT;
  bool motor_state;
};

typedef struct EAT_measurement Measurement;

void setup() 
{
  Serial.begin(9600);
  ADS.begin();
  pinMode(pin_DET, INPUT);
  pinMode(pin_CS, OUTPUT);

  while(!is_SD_in)
  {
    SD_init();
    delay(5000);
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
    check_config();
  }

  if(millis() - last_recording_check > 500)
  {
    curr_time = rtc.now().unixtime();
    
    if(is_recording && curr_time-last_sample_time > sample_rate * 60)
    {
      record_data();
    }

    last_recording_check = millis();

    //maybe also add something in here to check if the SD card was taken out
  }
}

int8_t record_data()
{
  //need to read sensor info
  //write data to the sd card
  //update the last sample time config file
  //Serial.println(curr_time);
  return 0;
}

//make sure all of the config files are where they need to be
void check_config()
{
  File _file;
  String _tmp = "";
  
  while(!is_SD_in)
  {
    SD_init();
  }
  
  //read through all of the config files
  //set the main variables based on that
  //if the config file is missing replace it with a new one with default values

  //get recording state
  _file = SD.open("config/recording state.config");

  if(!_file)
  {
    _file = SD.open("config/recording state.config", FILE_WRITE);
    _file.print(default_recording_state);
    _file.close();
    is_recording = default_recording_state;
  }
  else
  {
    _tmp = "";
  
    while(_file.available())
    {
      char _data = _file.read();
      _tmp += _data;
    }

    if(_tmp.toInt() == 1)
    {
      is_recording = true;
    }
    else
    {
      is_recording = false;
    }
  
    _file.close();
  }
  
  //get sample rate
  _file = SD.open("config/sample rate.config");

  if(!_file)
  {
    _file = SD.open("config/sample rate.config", FILE_WRITE);
    _file.print(default_sample_rate);
    _file.close();
    sample_rate = default_sample_rate;
  }
  else
  {
    _tmp = "";
  
    while(_file.available())
    {
      char _data = _file.read();
      _tmp += _data;
    }

    sample_rate = _tmp.toInt();
  
    _file.close();
  }

  //get recording name
  _file = SD.open("config/recording name.config");

  if(!_file)
  {
    _file = SD.open("config/recording name.config", FILE_WRITE);
    _file.print(default_recording_file_name);
    _file.close();
    recording_file_name = default_recording_file_name;
    return;
  }
  else
  {
    recording_file_name = "";
  
    while(_file.available())
    {
      char _data = _file.read();
      recording_file_name += _data;
    }
  
    _file.close();
  }
  
  //get last sample time
  _file = SD.open("config/last sample time.config");

  if(!_file)
  {
    _file = SD.open("config/last sample time.config", FILE_WRITE);
    _file.print(default_last_sample_time);
    _file.close();
    last_sample_time = default_last_sample_time;
  }
  else
  {
    _tmp = "";
  
    while(_file.available())
    {
      char _data = _file.read();
      _tmp += _data;
    }

    last_sample_time = _tmp.toInt();
  
    _file.close();
  }
  return;
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
