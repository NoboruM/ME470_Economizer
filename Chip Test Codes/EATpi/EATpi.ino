//MAIN code for running the EATPi
//This function contains the setup code, main loop code, and code relating to taking and storing data

//The libraries needed to run this code:
/*
 * https://www.arduino.cc/reference/en/libraries/sdfat/
 * https://github.com/RobTillaart/ADS1X15
 * https://github.com/adafruit/RTClib
 */

//The board library needed to upload to the Arduino Nano Every can be found in the board manager:
/*
 * Arduino megaAVR boards
 */

//declare the libraries
#include <SPI.h>
#include <SdFat.h>
#include "ADS1X15.h"
#include "RTClib.h"

//Create instances of each of the boards we are using 
SdFat SD;
ADS1115 ADS(0x48); //0x48 is the I2C address of the ADC
RTC_PCF8523 rtc;

//This variable is meant to be changed when Uploading the code
//If it is true, the motor light will turn on when it senses the right amount of vibration no matter what state the code is in
//If it is false, the motor detection will only run when data is recorded
//It is beneficial to set this to false because it will use less computing power when running the code
#define DEBUG_MOTOR true

//Defining some pins used by the Arduino
#define pin_CS 10 //chip select pin for the SD card reader
#define pin_DET 3 //detect pin for the SD card reader
#define pin_button 2 //button sense pin for the start/stop recording button
#define pin_LED_red 6 //the red LED will blink when a recording is happening
#define pin_LED_white 8 //the white LED will be on when the motor is detected if the DEBUG_MOTOR variable is true

//This pin defines the value of the static resistor used in the thermistor
#define R1 10000

//These are the values that the Arduino will set the config files to if they are not detected in the correct place
#define default_sample_rate 15
#define default_recording_state 0
#define default_last_sample_time 0
#define default_recording_file_name "tmp.csv"

//Steinhard and Hart Equation Coefficients for converting resistance to temperature
float A = 0.00103;
float B = 0.00024;
float C = 0.000000116956;

//boolean that stores the state of if the SD card is in or not
bool is_SD_in = false;

//Local variables which store information for the functioning of the device
bool is_recording = false;
bool is_recording_light_on = false;
uint16_t sample_rate = default_sample_rate;
unsigned long last_sample_time = default_last_sample_time;
String recording_file_name = default_recording_file_name;
unsigned long last_recording_check = 0;
unsigned long curr_time = 0;

//this is a data structure which stores the information for one data point
struct EAT_measurement
{
  unsigned long time_stamp;
  float OAT;
  float MAT;
  bool motor_state;
};

typedef struct EAT_measurement Measurement;

//This setup function runs once on powering on or restarting of the Arduino
void setup() 
{
  //start a serial port with a baudrate of 115200
  Serial.begin(115200);

  //start the ADC
  ADS.begin();

  //start the RTC
  rtc.begin();

  //set the mode of all of the hardware pins used in the code
  pinMode(pin_DET, INPUT);
  pinMode(pin_CS, OUTPUT);
  pinMode(pin_LED_red, OUTPUT);
  pinMode(pin_LED_white, OUTPUT);

  //This creates a pin interrupt for some of the functions
  //If the pin state is triggered, the function listed should run
  attachInterrupt(pin_button, change_recording_state, RISING); //if the pin button shows a rising signal, change the recording state
  attachInterrupt(pin_DET, SD_init, CHANGE); //If the SD card detection signal changes, update the SD card state

  //initialize the SD card
  SD_init();

  //If the SD card does not initialize, wait until it does
  while(!is_SD_in)
  {
    delay(5000);
    SD_init();
  }

  //Run the code that reads the config files from the SD card and changes the state of the variables
  check_config();
}

//this loop function runs repeatedly after the setup function
void loop() 
{
  //wait until a command can be read from incoming serial data
  if(Serial.available() > 0)
  {
    //parse the command
    parse_command();
  }

  //only continue with the data recording code if a recording is supposed to happen
  if(is_recording)
  {
    //only do the check every half second (as determined by the Arduino timer) to keep from calling the RTC too often
    if(millis() - last_recording_check > 500)
    {
      //get the current time from the RTC which we are using to determine when the sample should occur
      curr_time = rtc.now().unixtime();

      //If the time is not within the sample window, take a new sample
      if((curr_time-last_sample_time > (sample_rate * 60-1) || curr_time-last_sample_time < 0))
      {
        //execute the record data function and throw an error to the serial monitor if it doesn't work
        if(!record_data())
        {
          Serial.print("ER5\r\n");
        }
      }

      //update the recording red LED
      //Because of the earlier if statement, the LED will flash at 1 Hz
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

      //update the time of the last recording check
      last_recording_check = millis();

      //If the current way to check for SD card precense still isn't working, maybe also add something in here to check it
    }
  }
  
  //the DEBUG_MOTOR state will be updated when uploaded in order to see the motor debug light   
  //This function is useful for checking if the motor detection threshold is adequate for the site 
#if DEBUG_MOTOR
  //check the motor state and turn on the light if the system is detecting a running motor
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

//this function is called when data should be recorded to the SD card
//it returns true if it was sucessful and false if not
bool record_data()
{
  //open the data recording file with write privileges
  File _file = SD.open(recording_file_name, FILE_WRITE);

  //if there is no file return a failed condition
  if(!_file)
  {
    return false;
  }

  //update the last recording time on the SD card config file if it fails return a failed state
  if(cmd_s_lst(curr_time))
  {
    last_sample_time = curr_time;
  }
  else
  {
    return false;
  }

  //if the file is new, it will not have a header and have around 0 bytes so add the header before continuing
  if(_file.size() < 4)
  {
    _file.println("Date,OAT,MAT,Motor State");
  }

  //get the data from the measure function and store it in the measurement data structure
  Measurement _data = measure();

  //add the new data entry to the file
  _file.println(String(_data.time_stamp)+","+f2str(_data.OAT)+","+f2str(_data.MAT)+","+_data.motor_state);

  //close the file
  _file.close();

  return true;
}

//this function takes measurements from all of the sensors
//it returns a measurement in the measurement data structure defined at the top of this file
Measurement measure()
{
  //create the local measurement variable
  Measurement _data_out;

  //get the resistance of the thermistors
  int16_t _val_0 = ADS.readADC(0); //input 0 on the ADC measures the source voltage nominally 5v
  int16_t _val_1 = ADS.readADC(1); //input 1 on the ADC measures the output of the MAT voltage divider
  int16_t _val_3 = ADS.readADC(3); //input 3 on the ADC measures the output of the OAT voltage divider
  float _f = ADS.toVoltage(1);  // voltage factor used for converting above ints to voltages
  
  //get the above values as a voltage instead of as an int
  float _Vin = _val_0 * _f;
  float _Vout_1 = _val_1 * _f;
  float _Vout_3 = _val_3 * _f;

  //calculate the value of the thermistor resistance based on input voltage and voltage divider output
  float _ohms_1 = R1*(_Vin/_Vout_1 - 1);
  float _ohms_3 = R1*(_Vin/_Vout_3 - 1);

  //store all of the data
  _data_out.time_stamp = get_dt(); //get time stamp from the RTC
  _data_out.OAT = ohm_to_temp(_ohms_3); //convert the OAT resistance to temp
  _data_out.MAT = ohm_to_temp(_ohms_1); //convert the MAT resistance to temp
  _data_out.motor_state = get_motor_state(); //get the state of the motor from the vibration sensor

  return _data_out;
}

//this function converts resistances to temperatures using the Steinhart and Hart Equation
//this function takes a ristance and returns the temperature in farenheit
float ohm_to_temp(float _R)
{
  //calculate the temp in kelvin from resistance using the Steinhard and Hart Equation
  //the coefficients A, B, and C are defined at the stop of this document
  float _T = 1/(A + (B*log(_R)) + (C*(log(_R)*log(_R)*log(_R))));

  //convert the Kelvin temperature reading to Celcius
  float _Tc = _T - 273.15;

  //conver the Celcius to Fahrenheit
  float _Tf = (_Tc * 1.8) + 32;

  return _Tf;
}

//this function reads the vibration sensor to determine the motor state
//the function returns true if it thinks the motor is running and false if not
bool get_motor_state()
{
  //define local variables for determining the state
  int16_t _last_measurement = 0;
  int16_t _curr_measurement = ADS.readADC(2); //ADC pin 2 is used by the vibration sensor
  unsigned long _sum = 0;

  //take 25 samples and record the sum of the differences between samples
  //ideally, stronger vibrations create a stronger difference in readings as we have seen in testing
  for (int i = 0; i<25; i++)
  {
    _sum += abs(_curr_measurement-_last_measurement);
    _last_measurement = _curr_measurement;
    _curr_measurement = ADS.readADC(2);
    delay(10);
  }

  //caluclate the average of the change in values
  float _ans = _sum/25;

  //uncomment this to debug the values even more
  //Serial.println(_ans);

  //if the average difference is above a experimentally determined threshold, the motor is running
  //this number can be decreased to make this more sensitive to weaker vibrations or increased to do the opposite
  if(_ans > 150)
  {
    return true;
  }
  
  return false;
}

//this function initalizes the SD card and updates the variable that says if it is present or not
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

//convert float to string. Very useful for converting OAT/MAT data for storing on the SD card
//this function takes a float and returns a strong
String f2str(float _data)
{
  //truncate the decimals of the float
  String _tmp = String(float(round(_data * 10)) / 10.0);
  return _tmp.substring(0,_tmp.length()-1);
}

//this function returns the current EPOCH time stored by the RTC to be stored on the SD card
//it returns an unsigned long of whatever date the RTC says it is
unsigned long get_dt()
{
  unsigned long _time = rtc.now().unixtime();

  //we limit the date it can store to sometime in 2038 (the signed long limit) because it will overflow the raspberry pi
  if(_time > 2147483646)
  {
    _time = 2147483646;
  }
  
  return _time;
}

//this function is called when the start/stop recording button is pressed
void change_recording_state()
{
  if(is_recording)
  {
    //update the config file on the SD card too
    if(!cmd_s_rs_internal("0"))
    {
      return;
    }
    is_recording = false;
    digitalWrite(pin_LED_red, false);
  }
  else
  {
    if(!cmd_s_rs_internal("1"))
    {
      return;
    }
    is_recording = true;
  }
  return;
}
