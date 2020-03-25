#!/usr/bin/env python3
import ast
from datetime import datetime
import json
import serial
import time
import threading
import os

import paho.mqtt.client as mqtt
from xbee import ZigBee

BROKER_ADDR = '127.0.0.1'
BROKER_PORT = 1883
PORT = '/dev/ttyUSB0'
BAND_RATE = 9600
MAIN_TOPIC = 'iotomato/'


def handle_xbee(xbee_packet):
    try:
        payload_dit = ast.literal_eval((xbee_packet['rf_data']).decode('utf-8'))
        target = list(payload_dit.keys())[0]
        data_dit = payload_dit[target]
        device_id = data_dit['device_id']
        sub_topic = 'device/' + target + '/device_id/' + device_id
        mqtt_client.publish(MAIN_TOPIC + sub_topic, json.dumps(data_dit), 0)

    except UnicodeDecodeError:
        pass

    except ValueError:
        pass


mqtt_client = mqtt.Client(protocol=mqtt.MQTTv31)
mqtt_client.connect(host=BROKER_ADDR, port=BROKER_PORT, keepalive=60)

serial_port = serial.Serial(PORT, BAND_RATE)
xbee = ZigBee(serial_port, escaped=True, callback=handle_xbee)

try:
    mqtt_client.loop_forever()

except KeyboardInterrupt:
    mqtt_client.disconnect()
    xbee.halt()
    serial_port.close()
    exit(0)

