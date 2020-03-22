#include <SoftwareSerial.h>
#include "XBee.h"
#include "DHT.h"

#define DEVICE_ID 2
#define LIGHT_SENSOR_PIN A1
#define DHT_SENSOR_PIN 4
#define DHTTYPE DHT22
#define COORDINATOR_HIGH_ADDRESS 0x0013A200
#define COORDINATOR_LOW_ADDRESS  0x415411AB

XBee xbee = XBee();
DHT dht22 = DHT(DHT_SENSOR_PIN, DHTTYPE);
XBeeAddress64 addr64 = XBeeAddress64(COORDINATOR_HIGH_ADDRESS,  COORDINATOR_LOW_ADDRESS);


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


void setup()
{
  Serial.begin(9600);
  xbee.setSerial(Serial);
  dht22.begin();
  delay(100);
}



void loop()
{
  int start_time_m = millis();
  
  int   light       = analogRead(LIGHT_SENSOR_PIN);
  float temperature = dht22.readTemperature();
  float humidity    = dht22.readHumidity();
  
  char data_json[256];
  char temperature_str[16];
  char humidity_str[16];

  memset(data_json, 0, 256);
  memset(temperature_str, 0, 16);
  memset(humidity_str, 0, 16);
  
  convertFloatToChar(temperature_str, temperature);  
  convertFloatToChar(humidity_str, humidity);

  sprintf(data_json, "{'environment': {'device_id':\"%d\", 'temperature':%s, 'humidity':%s,'light':%d}}", DEVICE_ID, temperature_str, humidity_str, light);
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
