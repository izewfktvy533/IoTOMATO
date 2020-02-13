#!/usr/bin/env python3

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import ast
import logging
import time
import argparse
import json

import paho.mqtt.client as mqtt

AllowedActions = ['both', 'publish', 'subscribe']

AWS_HOST   = "a2jbwrz4hgj7v1-ats.iot.ap-northeast-1.amazonaws.com"
AWS_PORT   = 8883
CA_PATH    = "root-CA.crt"
CERT_PATH  = "iotomato.cert.pem"
KEY_PATH   = "iotomato.private.key"
MAIN_TOPIC = "iotomato"
CLIENT_ID  = "IoTOMATO"

MQTT_BROKER_ADDR = 'localhost'
MQTT_BROKER_PORT = 1883


def onConnect(client, userdata, flags, response_code):
    client.subscribe("iotomato/#", qos=0)


def onMessage(client, user_data, msg):
    print(msg.topic)
    print(msg.payload)

    device_str = msg.topic.split('/')[1]
    data_str = msg.payload.decode('utf-8')
        
    data_dit = ast.literal_eval(data_str)
    payload_dit = {}
    payload_dit['timestamp'] =  data_dit['timestamp']
    payload_dit['device'] = device_str
    payload_dit.update(data_dit[device_str])
    
    user_data.publish(MAIN_TOPIC, json.dumps(payload_dit), 0)


# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicPubSub",
                    help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="sdk/test/Python", help="Targeted topic")
parser.add_argument("-m", "--mode", action="store", dest="mode", default="both",
                    help="Operation modes: %s"%str(AllowedActions))
parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World!",
                    help="Message to publish")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
useWebsocket = args.useWebsocket

clientId = args.clientId
topic = args.topic

clientId = CLIENT_ID
topic    = MAIN_TOPIC


if args.mode not in AllowedActions:
    parser.error("Unknown --mode option %s. Must be one of %s" % (args.mode, str(AllowedActions)))
    exit(2)

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Port defaults
if args.useWebsocket and not args.port:  # When no port override for WebSocket, default to 443
    port = 443
if not args.useWebsocket and not args.port:  # When no port override for non-WebSocket, default to 8883
    port = 8883

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()

myAWSIoTMQTTClient.publish(topic, "test", 1)


client = mqtt.Client(protocol=mqtt.MQTTv31, userdata=myAWSIoTMQTTClient)
client.on_connect = onConnect
client.on_message = onMessage
client.connect(host=MQTT_BROKER_ADDR, port=MQTT_BROKER_PORT, keepalive=60)

client.loop_forever()

