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
PORT = '/dev/ttyUSB1'
BAND_RATE = 9600
MAIN_TOPIC = 'iotomato/'


def send_to_mqtt_broker(sub_topic_str, payload_dit):
    mqtt_client.publish(MAIN_TOPIC + sub_topic_str, json.dumps(payload_dit), 0)


def handle_xbee(xbee_packet):
    try:
        payload_dit = ast.literal_eval((xbee_packet['rf_data']).decode('utf-8'))
        sub_topic_str = payload_dit['device']

        thread_send_to_mqtt_broker = threading.Thread(target=send_to_mqtt_broker, args=(sub_topic_str, payload_dit))
        thread_send_to_mqtt_broker.start()
        thread_send_to_mqtt_broker.join()

    except UnicodeDecodeError:
        pass

    except ValueError:
        pass


mqtt_client = mqtt.Client(protocol=mqtt.MQTTv31)
mqtt_client.connect(host=BROKER_ADDR, port=BROKER_PORT, keepalive=60)

serial_port = serial.Serial(PORT, BAND_RATE)
xbee = ZigBee(serial_port, escaped=True, callback=handle_xbee)

try:
    while True:
        time.sleep(0.001)

except KeyboardInterrupt:
    mqtt_client.disconnect()
    xbee.halt()
    serial_port.close()
    exit(0)


