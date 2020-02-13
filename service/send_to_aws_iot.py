#!/usr/bin/env python3

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import ast
import logging
import time
import argparse
import json

import paho.mqtt.client as mqtt

AWS_HOST   = "a2jbwrz4hgj7v1-ats.iot.ap-northeast-1.amazonaws.com"
AWS_PORT   = 8883
CA_PATH    = "/home/pi/workspace/IoTOMATO/service/aws_iot/root-CA.crt"
KEY_PATH   = "/home/pi/workspace/IoTOMATO/service/aws_iot/iotomato.private.key"
CERT_PATH  = "/home/pi/workspace/IoTOMATO/service/aws_iot/iotomato.cert.pem"
MAIN_TOPIC = "iotomato"
CLIENT_ID  = "IoTOMATO"

MQTT_BROKER_ADDR = 'localhost'
MQTT_BROKER_PORT = 1883


def onConnect(client, userdata, flags, response_code):
    client.subscribe("iotomato/#", qos=0)


def onMessage(client, user_data, msg):
    device_str = msg.topic.split('/')[1]
    data_str = msg.payload.decode('utf-8')
        
    data_dit = ast.literal_eval(data_str)
    payload_dit = {}
    payload_dit['timestamp'] =  data_dit['timestamp']
    payload_dit['device'] = device_str
    payload_dit.update(data_dit[device_str])
    
    user_data.publish(MAIN_TOPIC, json.dumps(payload_dit), 0)


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

client = mqtt.Client(protocol=mqtt.MQTTv31, userdata=myAWSIoTMQTTClient)
client.on_connect = onConnect
client.on_message = onMessage
client.connect(host=MQTT_BROKER_ADDR, port=MQTT_BROKER_PORT, keepalive=60)

client.loop_forever()

