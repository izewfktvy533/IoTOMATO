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


def send_to_mqtt_broker(sub_topic_str, data_dit):
    device_str = sub_topic_str

    payload_dit = {}
    payload_dit['timestamp'] =  data_dit['timestamp']
    payload_dit['device'] = device_str
    payload_dit.update(data_dit[device_str])
     
    mqtt_client.publish(MAIN_TOPIC + sub_topic_str, json.dumps(payload_dit), 1)


def handle_xbee(xbee_packet):
    timestamp_datetime = datetime.now()
    timestamp_str = timestamp_datetime.strftime("%Y/%m/%d %H:%M:%S")
    file_name_str = timestamp_datetime.strftime("%Y-%m-%d") + ".json"

    try:
        payload_dit = dict()
        data_dit = ast.literal_eval((xbee_packet['rf_data']).decode('utf-8'))
        payload_dit.update(data_dit)
        sub_topic_str = list(payload_dit.keys())[0]
        payload_dit.update({'timestamp' : timestamp_str})
        directory_name_str = sub_topic_str

        print(payload_dit)

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


