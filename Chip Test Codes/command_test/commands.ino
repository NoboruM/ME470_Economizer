void parse_command()
{
  unsigned long serial_start_time = millis();
  String command = "";
  bool is_command_ending = false;
  
  while(1)
  {
    if(Serial.available() > 0)
    {
      char c = Serial.read();
      command += c;

      if(is_command_ending && c == 10)
      {
        break;
      }
      
      if(c == 13)
      {
        is_command_ending = true;
      }
      else
      {
        is_command_ending = false;
      }
    }

    if(millis() - serial_start_time > 5000)
    {
      return_action(4);
      return;
    }
  }

  //act on it

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

  //read file data
  if(command.indexOf("-g=") == 0)
  {
    return_action(cmd_g_d(command.substring(3, command.length()-2)));
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
    return;
  }
  
  //set the recording file
  if(command.indexOf("-n=") == 0)
  {
    return_action(cmd_s_fn(command.substring(3, command.length()-2)));
    return;
  }
  
  //set the date and time
  if(command.indexOf("-t=") == 0)
  {
    return_action(cmd_s_dt(command.substring(3, command.length()-2)));
    return;
  }
  
  return_action(1);
}

void return_action(int8_t _input)
{
  switch (_input)
  {
    case -1:
      Serial.print("\r\n");
      break;
    case 0:
      Serial.write("AOK\r\n");
      break;
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

//this command is for checking whether the arduino is able to communicate with the raspberry pi
int8_t cmd_ping()
{
  return 0;
}

//this command is for getting the sampling rate of the arduino
int8_t cmd_g_sr()
{
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  File _file = SD.open("config/sample rate.config");

  if(!_file)
  {
    if(cmd_s_sr(default_sample_rate) != 0)
    {
      return 5;
    }
  }

  _file = SD.open("config/sample rate.config");

  while(_file.available())
  {
    char _data = _file.read();
    Serial.write(_data);
  }

  _file.close();

  return -1;
}

//this command is for setting the sampling rate of the arduino
int8_t cmd_s_sr(String _sample_rate)
{
  //make sure the paramters are valid
  if(_sample_rate.toInt() <= 0)
  {
    return 2;
  }
  
  //make sure the SD card is there
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  //remove the old one
  SD.remove("config/sample rate.config");

  //make the new one
  File _file = SD.open("config/sample rate.config", FILE_WRITE);

  if(!_file)
  {
    return 3;
  }

  //printout the sample rate
  _file.print(_sample_rate);

  _file.close();
  
  return 0;
}

int8_t cmd_g_rs()
{
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  File _file = SD.open("config/recording state.config");

  if(!_file)
  {
    if(cmd_s_rs(default_recording_state) != 0)
    {
      return 5;
    }
  }

  _file = SD.open("config/recording state.config");

  while(_file.available())
  {
    char _data = _file.read();
    Serial.write(_data);
  }

  _file.close();

  return -1;
}

int8_t cmd_s_rs(String _recording_state)
{
  //make sure the paramters are valid
  if(_recording_state != "0" && _recording_state != "1")
  {
    return 2;
  }
  
  //make sure the SD card is there
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  //remove the old one
  SD.remove("config/recording state.config");

  //make the new one
  File _file = SD.open("config/recording state.config", FILE_WRITE);

  if(!_file)
  {
    return 3;
  }

  //printout the sample rate
  _file.print(_recording_state);

  _file.close();
  
  return 0;
}

//this command is for getting the data from a file
int8_t cmd_g_d(String _file_name)
{
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
  unsigned long _num_lines = 0;

  //if there is no file give a parameter error
  if(!_file)
  {
    return 2;
  }
  /*
  //read out data from the file
  while(_file.available())
  {
    char _data = _file.read();
    if (_data == '\n')
    {
      _num_lines ++;
    }
  }

  Serial.print("size="+String(_num_lines)+"\n");

  _file.close();
  
  //open the file
  _file = SD.open(_file_name);

  //if there is no file give a parameter error
  if(!_file)
  {
    return 2;
  }
  */
  //read out data from the file
  while(_file.available())
  {
    char _data = _file.read();
    Serial.write(_data);
  }

  _file.close();
  
  return -1;
}

//this command is for listing all of the files that are stored in the device besides the config file
int8_t cmd_g_fns()
{
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

  while(true) //loop through all entries and create a list of their names
  {
    //open the next file
    File _file = _dir.openNextFile();

    //make sure there is a file to read
    if(_file)
    {
      char _name[64];
      _file.getName(_name, 64);
      
      char* _csv_check = strstr(_name, ".csv");
      
      if(_csv_check != nullptr)
      {
        //add commas where they belong
        if(_file_count > 0 )
        {
          Serial.print(",");
        }
        _file_count ++;
        
        Serial.print(_name);
      }
    }
    else
    {
      break;
    }

    _file.close();
  }
  
  return -1;
}

int8_t cmd_g_fn()
{
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  File _file = SD.open("config/recording name.config");

  if(!_file)
  {
    return 5;
  }

  while(_file.available())
  {
    char _data = _file.read();
    Serial.write(_data);
  }

  _file.close();

  return -1;
}

int8_t cmd_s_fn(String _file_name)
{
  //make sure the paramters are valid
  if(_file_name.length() - _file_name.indexOf(".csv") != 4)
  {
    return 2;
  }
  
  //make sure the SD card is there
  if(!is_SD_in)
  {
    SD_init();
  }

  if(!is_SD_in)
  {
    return 3;
  }

  //remove the old one
  SD.remove("config/recording name.config");

  //make the new one
  File _file = SD.open("config/recording name.config", FILE_WRITE);

  if(!_file)
  {
    return 3;
  }

  //printout the sample rate
  _file.print(_file_name);

  _file.close();
  
  return 0;
}

int8_t cmd_g_dt()
{
  unsigned long _time = 0;

  _time = rtc.now().unixtime();

  if(_time == 0)
  {
    return 5;
  }
  
  Serial.print(_time);
  return -1;
}

int8_t cmd_s_dt(String _date_time)
{
  short _partial = 0;
  
  //Convert a string to a long in a very fun way
  for (int i = _date_time.length()-1; i >= 0; i -= 1)
  {
    _partial = _date_time.charAt(i) - '0';

    if(_partial < 0 || _partial > 9)
    {
      return 5;
    }
  }

  unsigned long _time = _date_time.toInt();

  rtc.adjust(_time);

  return 0;
}

int8_t cmd_g_ld()
{
  Measurement _data = measure();

  Serial.print(String(_data.time_stamp)+","+String(_data.OAT)+","+String(_data.MAT)+","+String(_data.motor_state));

  return -1;
}
