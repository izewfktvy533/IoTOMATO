#include <SoftwareSerial.h>
#include "XBee.h"
#include "DHT.h"
#include "HP20x_dev.h"
#include "Ultrasonic.h"

#define CO2_SENSOR S_SERIAL
#define LIGHT_SENSOR_PIN A1
#define DHT_SENSOR_PIN 4
#define ULTRASONIC_SENSOR_PIN 8
#define DHTTYPE DHT22
#define COORDINATOR_HIGH_ADDRESS 0x00000000
#define COORDINATOR_LOW_ADDRESS  0x0000FFFF


XBee xbee = XBee();
SoftwareSerial S_SERIAL(2, 3);
Ultrasonic ultrasonic(ULTRASONIC_SENSOR_PIN);
DHT dht22 = DHT(DHT_SENSOR_PIN, DHTTYPE);
XBeeAddress64 addr64 = XBeeAddress64(COORDINATOR_HIGH_ADDRESS,  COORDINATOR_LOW_ADDRESS);

const unsigned char CMD_FOR_CO2_SENSOR[] =
{
  0xff, 0x01, 0x86, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x79
};



inline void convertFloatToChar(char* str, float value)
{
    int whl;
    unsigned int frac;
    boolean inverse = false; //符号
 
    whl = (int)value;                //整数
    frac = (unsigned int)(value * 100) % 100; //少数
 
    if(whl < 0){
        whl *= -1;
        inverse = true;
    }
 
    if(inverse == true){
        sprintf(str, "-%d.%02d", whl, frac);
    }else{
        sprintf(str, "%d.%02d", whl, frac);
    }

}



inline int get_co2_ppm()
{
  byte data[9];
  memset(data, 0, 9);

  for(int i=0; i<sizeof(CMD_FOR_CO2_SENSOR); i++)
  {
    CO2_SENSOR.write(CMD_FOR_CO2_SENSOR[i]);
  }
  delay(200);
  
  if(CO2_SENSOR.available())
  {
    while(CO2_SENSOR.available())
    {
      for(int i=0;i<9; i++)
      {
        data[i] = CO2_SENSOR.read();
      }
    } 
  }
  
  return (int)data[2] * 256 + (int)data[3];
}



void setup()
{
  Serial.begin(9600);
  CO2_SENSOR.begin(9600);
  xbee.setSerial(Serial);
  dht22.begin();
  HP20x.begin();
  delay(100);
}



void loop()
{
  int start_time_m = millis();
  
  int   light            = analogRead(LIGHT_SENSOR_PIN);
  int   co2_ppm          = get_co2_ppm();
  int   water_level      = ultrasonic.MeasureInCentimeters();
  float air_temperature  = dht22.readTemperature();
  float air_humidity     = dht22.readHumidity();
  float air_pressure     = HP20x.ReadPressure() / 100.0;
  
  char data_json[256];
  char air_temperature_str[16];
  char air_humidity_str[16];
  char air_pressure_str[16];

  memset(data_json, 0, 256);
  memset(air_temperature_str, 0, 16);
  memset(air_humidity_str, 0, 16);
  memset(air_pressure_str, 0, 16);  
  
  convertFloatToChar(air_temperature_str, air_temperature);  
  convertFloatToChar(air_humidity_str, air_humidity);
  convertFloatToChar(air_pressure_str, air_pressure);
  
  sprintf(data_json, "{'vinyl_house':{'light':%d, 'air_temperature':%s, 'air_humidity':%s, 'air_pressure':%s, 'co2_ppm':%d, 'water_level':%d}}", light, air_temperature_str, air_humidity_str, air_pressure_str, co2_ppm, water_level);
  Serial.println(data_json);
  
  ZBTxRequest zbTx = ZBTxRequest(addr64, data_json, strlen(data_json));
  xbee.send(zbTx);
  
  /*** mesuring run time ***/
  int finish_time_m = millis();
  /*
  Serial.print(finish_time_m - start_time_m);
  Serial.print(" + ");
  */
  int delta = finish_time_m - start_time_m;

  if (delta < 3000) {
    delay(3000 - delta);
  }

}
