#!/usr/bin/env python3
import ast
from datetime import datetime
import json
import serial
import time
import threading
import os

from xbee import ZigBee
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient


AWS_HOST   = "a2jbwrz4hgj7v1-ats.iot.ap-northeast-1.amazonaws.com"
AWS_PORT   = 8883
CA_PATH    = "/home/pi/workspace/IoTOMATO/gateway/aws_iot/root-CA.crt"
KEY_PATH   = "/home/pi/workspace/IoTOMATO/gateway/aws_iot/iotomato.private.key"
CERT_PATH  = "/home/pi/workspace/IoTOMATO/gateway/aws_iot/iotomato.cert.pem"
MAIN_TOPIC = "iotomato"
CLIENT_ID  = "IoTOMATO"
PORT = '/dev/ttyUSB0'
BAND_RATE = 9600
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


def send_mqtt_broker(sub_topic_str, data_dit):
    device_str = sub_topic_str

    payload_dit = {}
    payload_dit['timestamp'] =  data_dit['timestamp']
    payload_dit['device'] = device_str
    payload_dit.update(data_dit[device_str])
     
    myAWSIoTMQTTClient.publish(MAIN_TOPIC, json.dumps(payload_dit), 0)


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

        thread_send_mqtt_broker = threading.Thread(target=send_mqtt_broker, args=(sub_topic_str, payload_dit))
        thread_store_data = threading.Thread(target=store_data, args=(directory_name_str, file_name_str, payload_dit))

        thread_send_mqtt_broker.start()
        thread_store_data.start()

        thread_send_mqtt_broker.join()
        thread_store_data.join()

    except UnicodeDecodeError:
        pass

    except ValueError:
        pass


myAWSIoTMQTTClient = AWSIoTMQTTClient(CLIENT_ID)
myAWSIoTMQTTClient.configureEndpoint(AWS_HOST, AWS_PORT)
myAWSIoTMQTTClient.configureCredentials(CA_PATH, KEY_PATH, CERT_PATH)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()

serial_port = serial.Serial(PORT, BAND_RATE)
xbee = ZigBee(serial_port, escaped=True, callback=handle_xbee)


try:
    while True:
        time.sleep(0.000001)

except KeyboardInterrupt:
    myAWSIoTMQTTClient.disconnect()
    xbee.halt()
    serial_port.close()
    exit(0)


