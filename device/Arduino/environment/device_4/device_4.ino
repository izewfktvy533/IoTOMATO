#include <Wire.h>
#include "Seeed_BME280.h"
#include "XBee.h"

#define DEVICE_ID 4
#define COORDINATOR_HIGH_ADDRESS 0x0013A200
#define COORDINATOR_LOW_ADDRESS  0x415411AB

BME280 bme280;
XBee xbee = XBee();
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


void setup() {
    Serial.begin(9600);

    while(!bme280.init()) {
	    delay(100);
    }
}


void loop() {
    int start_time_m = millis();
    float temperature, humidity, pressure;
    char data_json[256];
    char temperature_str[16];
    char humidity_str[16];
    char pressure_str[16];

    temperature = bme280.getTemperature();
    humidity = bme280.getHumidity();
    pressure = bme280.getPressure() / 100;
  
    memset(data_json, 0, 256);
    memset(temperature_str, 0, 16);
    memset(humidity_str, 0, 16);
    memset(pressure_str, 0, 16);  
    
    convertFloatToChar(temperature_str, temperature);  
    convertFloatToChar(humidity_str, humidity);
    convertFloatToChar(pressure_str, pressure);

    sprintf(data_json, "{'environment': {'device_id':\"%d\", 'temperature':%s, 'humidity':%s, 'pressure':%s}}",  DEVICE_ID, temperature_str, humidity_str, pressure_str);
    
    ZBTxRequest zbTx = ZBTxRequest(addr64, data_json, strlen(data_json));
    xbee.send(zbTx);
    
    int finish_time_m = millis();
    int delta = finish_time_m - start_time_m;
  
    if (delta < 1000) {
      delay(1000 - delta);
    }

}

