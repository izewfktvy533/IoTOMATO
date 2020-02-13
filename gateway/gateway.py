#!/usr/bin/env python3

import ast
from datetime import datetime
import json
import serial
import time
import threading
import os

from xbee import ZigBee
import paho.mqtt.client as mqtt


PORT = '/dev/ttyUSB0'
BAND_RATE = 9600
MQTT_BROKER_ADDR = 'localhost'
MQTT_BROKER_PORT = 1883
MAIN_TOPIC = "iotomato/"
DIRECTORY_NAME = "/home/pi/workspace/IoTOMATO/gateway/data/sensing_part/"


def store_data(directory_name_str, file_name_str, payload_dit):
    os.chdir(DIRECTORY_NAME)
    cpath = os.path.abspath("./")

    try:
        os.chdir(directory_name_str)

    except FileNotFoundError:
        os.mkdir(directory_name_str)
        os.chdir(directory_name_str)

    with open(file_name_str, 'a') as fp:
        json.dump(payload_dit, fp)
        fp.write("\n")

    os.chdir(cpath)


def send_mqtt_broker(sub_topic_str, payload_dit):
    mqtt_packet = json.dumps(payload_dit)
    mqtt_client.publish(MAIN_TOPIC + sub_topic_str, mqtt_packet, qos=0)


def handle_xbee(xbee_packet):
    timestamp_datetime = datetime.now()
    timestamp_str = timestamp_datetime.strftime("%Y-%m-%dT%H:%M:%S")
    file_name_str = timestamp_datetime.strftime("%Y-%m-%d") + ".json"

    try:
        payload_dit = dict()
        data_dit = ast.literal_eval((xbee_packet['rf_data']).decode('utf-8'))
        payload_dit.update(data_dit)
        sub_topic_str = list(payload_dit.keys())[0]
        payload_dit.update({'timestamp' : timestamp_str})
        directory_name_str = sub_topic_str

        thread_send_mqtt_broker = threading.Thread(target=send_mqtt_broker, args=(sub_topic_str, payload_dit))
        #thread_store_data = threading.Thread(target=store_data, args=(directory_name_str, file_name_str, payload_dit))

        thread_send_mqtt_broker.start()
        #thread_store_data.start()

        thread_send_mqtt_broker.join()
        #thread_store_data.join()

    except UnicodeDecodeError:
        pass

    except ValueError:
        pass


if __name__ == '__main__':
    serial_port = serial.Serial(PORT, BAND_RATE)

    mqtt_client = mqtt.Client(protocol=mqtt.MQTTv31)
    mqtt_client.connect(host=MQTT_BROKER_ADDR, port=MQTT_BROKER_PORT, keepalive=60)

    xbee = ZigBee(serial_port, escaped=True, callback=handle_xbee)


    try:
        while True:
            time.sleep(0.000001)

    except KeyboardInterrupt:
        mqtt_client.disconnect()
        xbee.halt()
        serial_port.close()
        exit(1)

