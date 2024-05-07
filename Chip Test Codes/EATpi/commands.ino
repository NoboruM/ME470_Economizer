//This file contains commands related to parsing and executing commands coming through the serial connection

//the parse_command function is called when serial data is received
void parse_command()
{
  unsigned long serial_start_time = millis(); //this time will be used if needed to time out the serial connection
  String command = ""; //this will store the read command
  bool is_command_ending = false; //this will be true when a \r character is read indicating the command could end with a \n character next

  //loop until either the command is fully read or the process times out
  while(1)
  {
    //if there is a byte available to read, read it and do something
    if(Serial.available() > 0)
    {
      char c = Serial.read();
      command += c; //add the new character to the command string

      //if the new character was \n and \r was detected as the character before, stop reading waiting for more bytes
      if(is_command_ending && c == 10)
      {
        break;
      }

      //if \r is detected set the flag that the command could be ending with the next character
      if(c == 13)
      {
        is_command_ending = true;
      }
      else
      {
        is_command_ending = false;
      }
    }

    //if enough time has passed since we started reading bytes, time out the process
    if(millis() - serial_start_time > 5000)
    {
      return_action(4); //return error 4
      return;
    }
  }

  //act on whatever command was detected
  //each of these if statements use substrings and string lengths to figure out what the command is
  //they then run the command function which always starts with "cmd_"
  //if the command needs to return a status, it is returned using the return action command
  //sometimes, the check config function is called after a command. This reads and updates all of the config files incase something has changed
  //then the parse command function ends
  
  //ping command
  if(command.indexOf("-p?\r\n") != -1 && command.length() == 5)
  {
    return_action(cmd_ping());
    return;
  }

  //get file names command
  if(command.indexOf("-g?\r\n") != -1 && command.length() == 5)
  {
    return_action(cmd_g_fns());
    return;
  }

  //get sample rate
  if(command.indexOf("-f?\r\n") != -1 && command.length() == 5)
  {
    return_action(cmd_g_sr());
    return;
  }

  //get recording state
  if(command.indexOf("-s?\r\n") != -1 && command.length() == 5)
  {
    return_action(cmd_g_rs());
    return;
  }

  //get recording name
  if(command.indexOf("-n?\r\n") != -1 && command.length() == 5)
  {
    return_action(cmd_g_fn());
    return;
  }

  //get date time
  if(command.indexOf("-t?\r\n") != -1 && command.length() == 5)
  {
    return_action(cmd_g_dt());
    return;
  }
  
  //get live data
  if(command.indexOf("-d?\r\n") == 0 && command.length() == 5)
  {
    return_action(cmd_g_ld());
    return;
  }
  
  //get the list of file parameters
  if(command.indexOf("-x?\r\n") == 0 && command.length() == 5)
  {
    return_action(cmd_g_fps());
    return;
  }

  //read file data
  if(command.indexOf("-g=") == 0)
  {
    return_action(cmd_g_d(command.substring(3, command.length()-2)));
    return;
  }

  //read parameter data
  if(command.indexOf("-x=") == 0)
  {
    return_action(cmd_g_fp(command.substring(3, command.length()-2)));
    return;
  }

  //set the sample rate
  if(command.indexOf("-f=") == 0)
  {
    return_action(cmd_s_sr(command.substring(3, command.length()-2)));
    return;
  }
  
  //set the sample rate
  if(command.indexOf("-s=") == 0)
  {
    return_action(cmd_s_rs(command.substring(3, command.length()-2)));
    check_config();
    return;
  }
  
  //set the recording file
  if(command.indexOf("-n=") == 0)
  {
    return_action(cmd_s_fn(command.substring(3, command.length()-2)));
    check_config();
    return;
  }
  
  //set the date and time
  if(command.indexOf("-t=") == 0)
  {
    return_action(cmd_s_dt(command.substring(3, command.length()-2)));
    check_config();
    return;
  }
  
  //set the date and time
  if(command.indexOf("-p=") == 0)
  {
    return_action(cmd_s_fp(command.substring(3, command.length()-2)));
    check_config();
    return;
  }

  //if no command is recognized, return a command error response
  return_action(1);
}

//this function handles sending out status bytes over serial
//it takes in a number representing what message it should send over serial
void return_action(int8_t _input)
{
  switch (_input)
  {
    case -1: //it should just send the end message characters
      Serial.print("\r\n");
      break;
    case 0: //it should send the successful command status
      Serial.write("AOK\r\n"); 
      break;

    //the next ones are all errors
    case 1:
      Serial.write("ER1\r\n");
      break;
    case 2:
      Serial.write("ER2\r\n");
      break;
    case 3:
      Serial.write("ER3\r\n");
      break;
    case 4:
      Serial.write("ER4\r\n");
      break;
    default:
      Serial.write("ER5\r\n");
      break;
  }

  return;
}

//this is the pin command
//it should always return "AOK" to test if the Serial connection is working
int8_t cmd_ping()
{
  return 0;
}

//this command gets the sample rate of the arduino
//it will return the sample rate over the serial connection
int8_t cmd_g_sr()
{
  //check if the SD card is present twice to be safe
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  //open the correct config file
  File _file = SD.open("config/sample rate.config");

  //if there is no config file present, create a new one and set it to the defaul sample rate
  if(!_file)
  {
    if(cmd_s_sr(String(default_sample_rate)) != 0)
    {
      return 5; //if this still fails throw an error
    }
  }

  //make sure the file is open
  _file = SD.open("config/sample rate.config");

  //read all of the data on the file and print it out over the serial connection
  while(_file.available())
  {
    char _data = _file.read();
    Serial.write(_data);
  }

  //close the file
  _file.close();

  return -1;
}

//this command is for setting the sampling rate of the arduino
//this command takes a String containing the new sample rate
//this command will return "AOK" on success or an error if it fails
int8_t cmd_s_sr(String _sample_rate)
{
  //make sure the paramters are valid
  //this should only allow the program to continue if the value is an integer greater than 1
  //this should also account for if there are letters or decimals in the string
  if(_sample_rate.toInt() <= 0)
  {
    return 2;
  }
  
  //check if the SD card is present twice to be safe
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  //remove the old sample rate config file
  SD.remove("config/sample rate.config");

  //make the new one to replace it with
  File _file = SD.open("config/sample rate.config", FILE_WRITE);

  //if the file doesn't open there is a bigger problem
  if(!_file)
  {
    return 3;
  }

  //printout the sample rate into the config file
  _file.print(_sample_rate);

  //close the file
  _file.close();
  
  return 0;
}

//this command is used to get the recording state config file
//it will print out the contents of this config file over the serial connection
int8_t cmd_g_rs()
{
  //check if the SD card is present twice to be safe
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  //try to open the file
  File _file = SD.open("config/recording state.config");

  //if it fails, create a new file with the default recording state
  if(!_file)
  {
    if(cmd_s_rs(String(default_recording_state)) != 0)
    {
      return 5; //if this fails throw an error
    }
  }

  //open the file again incase a new one was created
  //should this be in the if statement above?
  _file = SD.open("config/recording state.config");

  //read out all the data and print it over the serial connection
  while(_file.available())
  {
    char _data = _file.read();
    Serial.write(_data);
  }

  //close the file
  _file.close();

  return -1; //this will make it print \r\n when done
}

//this command is used to set the recording state in the config file
//this command takes in a string of the desired recording state
//it will return either "AOK" or an error depending on what happens
int8_t cmd_s_rs(String _recording_state)
{
  //make sure the paramters sent in are valid: the state can be only 0 or 1
  if(_recording_state != "0" && _recording_state != "1")
  {
    return 2;
  }
  
  //check if the SD card is present twice to be safe
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  //remove the old recording state config file
  SD.remove("config/recording state.config");

  //make the new one to replace it
  File _file = SD.open("config/recording state.config", FILE_WRITE);

  //if the file doesn't open throw an error
  if(!_file)
  {
    return 3;
  }

  //print the new sample rate to the file
  _file.print(_recording_state);

  //close the file
  _file.close();
  
  return 0;
}

//this command is used to get data from a file stored on the SD card
//the command takes in a string of the file name desired to read
//the command returns all of the data over the serial connection
int8_t cmd_g_d(String _file_name)
{
  //check if the SD card is present twice to be safe
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }
  
  //open the file
  File _file = SD.open(_file_name);

  //if there is no file give a parameter error
  if(!_file)
  {
    return 2;
  }

  //print out the size of the file in bytes first which can be used to create a loading bar on the raspberry pi
  Serial.print("size=");Serial.print(_file.size());Serial.print("\n");
  
  //read out all the data from the file
  while(_file.available())
  {
    char _data = _file.read();
    Serial.write(_data);
  }

  //close the file
  _file.close();
  
  return -1;
}

//this command is used to get the data from a parameter file
//this command takes in the name of a parameter file to read
//the command will return the data inside the file over the serial connection
int8_t cmd_g_fp(String _file_name)
{
  //check if the SD card is present twice to be safe
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  //open the file
  File _file = SD.open("/params/" + _file_name);

  //if there is no file give a parameter error
  if(!_file)
  {
    return 2;
  }
  
  //read out data from the file
  while(_file.available())
  {
    char _data = _file.read();
    Serial.write(_data);
  }

  //close the file
  _file.close();
  
  return -1;
}

//this command is used to list out all of the csv files stored on the SD card
//the command returns all of the csv files it can find on the SD card over the serial connection
int8_t cmd_g_fns()
{
  //check if the SD card is present twice to be safe
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  //open the main folder of the SD card
  File _dir = SD.open("/");
  int _file_count = 0;

  //loop until there are no more files to read
  while(true)
  {
    //open the next file found in the directory
    File _file = _dir.openNextFile();

    //make sure there is a file to read
    if(_file)
    {
      //create a buffer to store the file name
      //this also does mean there should be a 64 character limit for naming files
      char _name[64];
      _file.getName(_name, 64); //get the file name and store it in the buffer

      //make sure the file name contains the .csv identifier
      //if it does not contain .csv it will return a nullptr
      char* _csv_check = strstr(_name, ".csv");

      //if it is indeed a csv file do the following
      if(_csv_check != nullptr)
      {
        //add commas before the name as long as its not the first file read
        if(_file_count > 0 )
        {
          Serial.print(",");
        }

        //increemnt the file counter
        _file_count ++;

        //print out the name over the Serial connection
        Serial.print(_name);
      }
    }
    else //if there is no more file to read, exit the loop
    {
      break;
    }

    //close the file
    _file.close();
  }
  
  return -1;
}

//this command is used to list out all of the parameter files stored on the SD card
int8_t cmd_g_fps()
{
  //check if the SD card is present twice to be safe
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  //open the params folder of the SD card
  File _dir = SD.open("/params/");
  int _file_count = 0;

  //loop until all of the files are checked
  while(true)
  {
    //open the next file found in the directory
    File _file = _dir.openNextFile();

    //make sure there is a file to read
    if(_file)
    {
      //create a buffer to store the file name
      //this also does mean there should be a 64 character limit for naming files
      char _name[64];
      _file.getName(_name, 64); //get the file name and store it in the buffer

      //check if the file name contains the .param identifier
      //if it is not a .param file it should return a nullptr
      char* _param_check = strstr(_name, ".param");

      //if it is indeed a param file
      if(_param_check != nullptr)
      {
        //add a comment before it if it is not the first name listed
        if(_file_count > 0 )
        {
          Serial.print(",");
        }

        //increment the param file counter
        _file_count ++;

        //print the name of the file to the serial connection
        Serial.print(_name);
      }
    }
    else //if there is no file to read end the loop
    {
      break;
    }

    //close the file
    _file.close();
  }
  
  return -1;
}

//this command is used to get the current file name the arduino is recording data to
//the file returns the name of the file over the serial connection
//unlike the other get commands, this command will not create a new file if there is none present, is this something that needs to be changed?
int8_t cmd_g_fn()
{
  //check if the SD card is present twice to be safe
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  //try to open the recording name file config
  File _file = SD.open("config/recording name.config");

  //if there is no file present return an error
  if(!_file)
  {
    return 5;
  }

  //read out all of the data and return it over the serial connection
  while(_file.available())
  {
    char _data = _file.read();
    Serial.write(_data);
  }

  //close the file
  _file.close();

  return -1;
}

//this command is used to set the file name that data on the Arduino should be recorded to
//it takes in a file name which is what the config file will be updated to
//it returns a status depending on what happens
int8_t cmd_s_fn(String _file_name)
{
  //make sure the paramters are valid by seeing if there is any information before the .csv file ending
  //also make sure .csv is included in the first place
  if(_file_name.length() - _file_name.indexOf(".csv") != 4 && _file_name.indexOf(".csv") > 0)
  {
    return 2;
  }
  
  //check if the SD card is present twice to be safe
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  //remove the old recording name config file
  SD.remove("config/recording name.config");

  //and replace it with a new one
  File _file = SD.open("config/recording name.config", FILE_WRITE);

  //if the file still doesnt exist, throw an error
  if(!_file)
  {
    return 3;
  }

  //add the data to the file
  _file.print(_file_name);

  //close the file
  _file.close();
  
  return 0;
}

//this command is used to get the date and time from the RTC
//it will return the signed long version of the epoch time over the serial connection
int8_t cmd_g_dt()
{
  unsigned long _time = 0;

  //get the date and time from the function in EATPI.ino
  _time = get_dt();

  //if the time seems invalid throw an error
  if(_time == 0)
  {
    return 5;
  }

  //send the time over the serial connection
  Serial.print(_time);
  return -1;
}

//this command is used to set the date and time of the RTC
//the function takes in the epoch time we want to set the RTC to. This can be an unsigned long
//the function will return a status byte depending on what happens
int8_t cmd_s_dt(String _date_time)
{
  //this just stores the current byte that is being read as a number
  short _partial = 0;
  
  //make sure that the new date and time does not have any invalid characters
  for (int i = _date_time.length()-1; i >= 0; i -= 1)
  {
    _partial = _date_time.charAt(i) - '0';

    //if the character is ever invalid, return an error
    if(_partial < 0 || _partial > 9)
    {
      return 5;
    }
  }

  //convert the string to an unsigned long
  unsigned long _time = _date_time.toInt();

  //adjust the RTC to the new epoch time
  rtc.adjust(_time);

  return 0;
}

//this command is used to get live data from the Arduino. It is currently unused by the raspberry pi
//the command returns the same data that would be stored to a csv file when taking a sample over the serial connection
//the benefit of this, is that samples can be taken regardless of sample rate and instantly plotted
int8_t cmd_g_ld()
{
  //get the measurement data
  Measurement _data = measure();

  //print the measurement that was taken over the serial connection
  Serial.print(String(_data.time_stamp)+","+String(_data.OAT)+","+String(_data.MAT)+","+String(_data.motor_state));

  return -1;
}

//this command is used to set the last sample time config file
//the command takes in an unsigned long which signifies when the last sample was taken
//it returns an error unrelated to serial command since it is not called as a command 
//0 means the command failed, 1 means it succeeded
int8_t cmd_s_lst(unsigned long _last_sample_time)
{
  //check if the SD card is present twice to be safe
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 0;
  }

  //remove the old last sample time config file
  SD.remove("config/last sample time.config");

  //and replace it with a new one
  File _file = SD.open("config/last sample time.config", FILE_WRITE);

  //if it still doesnt work throw an erorr
  if(!_file)
  {
    return 0;
  }

  //printout the new last sample time into the file
  _file.print(_last_sample_time);

  //close the file
  _file.close();
  
  return 1;
}

//this command is used to create a new param file
//the function takes in a input containing both the file name and what the data to write to it is
//the function returns a status byte
int8_t cmd_s_fp(String _input)
{
  //unlike the other set functions, this one does not check the input to make sure it is valid
  //this is something that needs to be done in the future but it is a bit complex and we ran out of time
  
  //however this command does check that there is at least one comma which is a good thing
  if(_input.indexOf(',') == -1)
  {
    return 2;
  }
  
  //check if the SD card is present twice to be safe
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  //the file name is the first parameter sent through the input so we seperate it here
  String _file_name = _input.substring(0,_input.indexOf(','));

  //the rest of the input is everything after the first comma
  _input = _input.substring(_input.indexOf(',')+1);

  //delete the old parameter file of the same name if there is one
  SD.remove("/params/"+_file_name);

  //and make a new one
  File _file = SD.open("/params/"+_file_name, FILE_WRITE);

  //if that failed throw an error
  if(!_file)
  {
    return 3;
  }

  //printout the parameter to this file to save it for when it is retrieved
  _file.print(_input);

  //close the file
  _file.close();
  
  return 0;
}

//this command can be called to update all of the variables stored on the Arduino from the config files
//this is often called after a set variable command to make sure the variables are up to date
//this command eos not take in or return anything
void check_config()
{
  //setup some variables used below
  File _file;
  String _tmp = "";

  //continuously try to setup the SD card if it is not currently
  //this may be contributing to the SD card bug
  while(!is_SD_in)
  {
    SD_init();
    delay(5000);
  }
  
  //read through all of the config files
  //set the main variables based on that
  //if the config file is missing replace it with a new one with default values

  //get recording state
  _file = SD.open("config/recording state.config");

  //if there is no file create a new one
  if(!_file)
  {
    _file = SD.open("config/recording state.config", FILE_WRITE);
    _file.print(default_recording_state);
    _file.close();
    is_recording = default_recording_state;
  }
  else //otherwise read the data
  {
    _tmp = "";

    //read the file into the tmp string for processing
    while(_file.available())
    {
      char _data = _file.read();
      _tmp += _data;
    }

    //convert the string to an integer and if it equals "1" set the recording state to true
    if(_tmp.toInt() == 1)
    {
      is_recording = true;
    }
    else //in any other condition set the recording state to false
    {
      is_recording = false;
      digitalWrite(pin_LED_red, LOW);
      is_recording_light_on = false;
    }

    //close the file
    _file.close();
  }
  
  //get sample rate
  _file = SD.open("config/sample rate.config");

  if(!_file) //if there is no sample rate file create a new one with default settings
  {
    _file = SD.open("config/sample rate.config", FILE_WRITE);
    _file.print(default_sample_rate);
    _file.close();
    sample_rate = default_sample_rate;
  }
  else //if there is a file read it and process the data
  {
    //create a temp string to store the data
    _tmp = "";

    //read all of the data into the string
    while(_file.available())
    {
      char _data = _file.read();
      _tmp += _data;
    }

    //set the sample rate to what was read
    sample_rate = _tmp.toInt();

    //close the file
    _file.close();

    //there is no error handling for an invalid sample time here because we assume the config file is always valid
    //maybe add some if more error handling is needed
  }

  //get recording name
  _file = SD.open("config/recording name.config");

  if(!_file) //if there is not file create a new one with the default data
  {
    _file = SD.open("config/recording name.config", FILE_WRITE);
    _file.print(default_recording_file_name);
    _file.close();
    recording_file_name = default_recording_file_name;
    return;
  }
  else //if there is, process the data inside the file
  {
    //reset the recording file name
    recording_file_name = "";

    //and replace it with the data inside the config file
    while(_file.available())
    {
      char _data = _file.read();
      recording_file_name += _data;
    }

    //close the file
    _file.close();

    //again there is not error handling for the data in this config file
    //this could be a problem but we assume the config file is always valid
  }
  
  //get last sample time
  _file = SD.open("config/last sample time.config");

  if(!_file) //if there is no last sample time data replace it with the default which should just be 0
  {
    _file = SD.open("config/last sample time.config", FILE_WRITE);
    _file.print(default_last_sample_time);
    _file.close();
    last_sample_time = default_last_sample_time;
  }
  else //if there is a file get the data
  {
    //create a temporary string to store the data in
    _tmp = "";

    //read out all the data from the file
    while(_file.available())
    {
      char _data = _file.read();
      _tmp += _data;
    }

    //set the last sample time based on the data that was read
    last_sample_time = _tmp.toInt();

    //close the file
    _file.close();

    //again no error handling which might be important if we think the data in the config file could be bad
  }
  return;
}

//this command is used to set the recording state without a command
//the command takes in the new recording state 
//the command returns a boolean which is true if successful and false if not
bool cmd_s_rs_internal(String _recording_state)
{
  //check if the SD card is present twice to be safe
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return false;
  }

  //remove the old recording state config file
  SD.remove("config/recording state.config");

  //and replace it with the new one
  File _file = SD.open("config/recording state.config", FILE_WRITE);

  //if there is still no file return that the command failed
  if(!_file)
  {
    return false;
  }

  //if not print out the new recording state
  _file.print(_recording_state);

  //close the file
  _file.close();
  
  return true;

  //since this command is internal there is no error handling since a user cannot set the recording state using it
}
