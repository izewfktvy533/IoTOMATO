/***
 *  Water sensor WD-3-WET-5Y
 *  Analog read
 */
#include <stdio.h>
#include <SoftwareSerial.h>
#include <XBee.h>
#include "Wire.h"

#define DEVICE_ID 1
#define VWC_PIN A0
#define EC_PIN  A1
#define TEMP_PIN A2
#define PWR_PIN 9
#define XBee_wake 7
#define LED_PIN   13

XBee xbee = XBee();
XBeeAddress64 addr64 = XBeeAddress64(0x00000000, 0x0000FFFF);


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
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, HIGH);
  
  pinMode(PWR_PIN, OUTPUT); //WD-c power pin setting
  digitalWrite(PWR_PIN, LOW);  

  analogReference(INTERNAL);  //analog reference

  // wake up the XBee
  pinMode(XBee_wake, OUTPUT);
  digitalWrite(XBee_wake, LOW); // LOW = XBee wakes up

  digitalWrite(LED_PIN, LOW);
  delay(100);
  digitalWrite(LED_PIN, HIGH);
  delay(100);
}


void loop() {
  int start_time_m = millis();
  
  // put your main code here, to run repeatedly:
  // wake up the XBee
  pinMode(XBee_wake, OUTPUT); // put pin in a high impedence state
  digitalWrite(XBee_wake, LOW); //LOW = XBee ON
    
  digitalWrite(PWR_PIN, HIGH);
  delay(5000);

  //Get sensing data
  float VWCread = analogRead(VWC_PIN);
  float ECread = analogRead(EC_PIN);
  float TEMPread = analogRead(TEMP_PIN);
  
  digitalWrite(PWR_PIN, LOW);

  float vwc = (VWCread/1023) * 100;
  float ec = (ECread/1023) * 7;
  float temperature = ((TEMPread/1023) * 50) - 10;
  
  char json[256];
  char VWCread_char[16];
  char ECread_char[16];
  char TEMPread_char[16];
    
  memset(json, 0, 256);
  memset(VWCread_char, 0, 16);
  memset(ECread_char, 0, 16);
  memset(TEMPread_char, 0, 16);

  convertFloatToChar(VWCread_char, vwc);  
  convertFloatToChar(ECread_char, ec);
  convertFloatToChar(TEMPread_char, temperature);

  sprintf(json, "{'soil': {'device_id':\"%d\", 'vwc':%s, 'ec':%s, 'temperature':%s}}", DEVICE_ID, VWCread_char, ECread_char, TEMPread_char);

  ZBTxRequest zbTx = ZBTxRequest(addr64, json, strlen(json));
  xbee.send(zbTx);

  digitalWrite(XBee_wake, HIGH); // HIGH = +5V, XBee OFF

  digitalWrite(PWR_PIN, LOW);
  delay(100);
  digitalWrite(PWR_PIN, HIGH);

    
  /*** mesuring run time ***/
  int finish_time_m = millis();
  /*
  Serial.print(finish_time_m - start_time_m);
  Serial.print(" + ");
  */
  int delta = finish_time_m - start_time_m;

  if (delta < 6000) {
    delay(6000 - delta);
  }
  
}
