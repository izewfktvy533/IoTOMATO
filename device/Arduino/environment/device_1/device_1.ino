#include <SoftwareSerial.h>
#include "Digital_Light_TSL2561.h"
#include "XBee.h"
#include "DHT.h"
#include "HP20x_dev.h"
#include "Ultrasonic.h"

#define DEVICE_ID 1
#define TANK_HEIGHT 30
#define CO2_SENSOR S_SERIAL
#define DHT_SENSOR_PIN 4
#define ULTRASONIC_SENSOR_PIN 8
#define DHTTYPE DHT22
#define COORDINATOR_HIGH_ADDRESS 0x0013A200
#define COORDINATOR_LOW_ADDRESS  0x415411AB

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


inline int get_co2()
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
  TSL2561.init();
  delay(100);
}



void loop()
{
  int start_time_m = millis();
  
  int   light       = TSL2561.readVisibleLux();
  int   co2         = get_co2();
  int   water_level = TANK_HEIGHT - ultrasonic.MeasureInCentimeters();
  float temperature = dht22.readTemperature();
  float humidity    = dht22.readHumidity();
  float pressure    = HP20x.ReadPressure() / 100.0;
  
  char data_json[256];
  char temperature_str[16];
  char humidity_str[16];
  char pressure_str[16];

  memset(data_json, 0, 256);
  memset(temperature_str, 0, 16);
  memset(humidity_str, 0, 16);
  memset(pressure_str, 0, 16);  
  
  convertFloatToChar(temperature_str, temperature);  
  convertFloatToChar(humidity_str, humidity);
  convertFloatToChar(pressure_str, pressure);;

  sprintf(data_json, "{'environment': {'device_id':\"%d\", 'temperature':%s, 'humidity':%s, 'pressure':%s, 'light':%d, 'co2':%d, 'water_level':%d}}", DEVICE_ID, temperature_str, humidity_str, pressure_str, light, co2, water_level);
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
