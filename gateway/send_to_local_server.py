#!/usr/bin/env python3
import json
import serial
import struct
import paho.mqtt.client as mqtt

from xbee import ZigBee

PORT = '/dev/ttyUSB1'
BAND_RATE = 9600
SERIAL_PORT = serial.Serial(PORT, BAND_RATE)
BROKER_ADDR = '127.0.0.1'
BROKER_PORT = 1883
XBEE_CDR_MAC = 0x13A20041629A7E
TOPIC = 'iotomato/#'


def onConnect(mqtt_client, user_data, flags, response_code):
    mqtt_client.subscribe(TOPIC, qos=0)


def onMessage(publisher, user_data, msg):
    xbee.send('tx', dest_addr_long=struct.pack('>q', XBEE_CDR_MAC), data=msg.payload)


xbee = ZigBee(SERIAL_PORT, escaped=True)
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv31)
mqtt_client.on_connect = onConnect
mqtt_client.on_message = onMessage
mqtt_client.connect(host=BROKER_ADDR, port=BROKER_PORT, keepalive=60)

try:
    mqtt_client.loop_forever()

except Exception:
    xbee.halt()
    SERIAL_PORT.close()
    mqtt_client.disconnect()
    exit(0)

