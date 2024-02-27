#define pin_INPUT A2

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(pin_INPUT, INPUT);
  
  while (!Serial)
  {
    delay(1000);
  }
}

void loop() 
{
  // put your main code here, to run repeatedly:
  Serial.println(analogRead(pin_INPUT));
  delay(500);
}
