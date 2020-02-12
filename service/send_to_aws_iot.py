#!/usr/bin/env python3
import ast
import json
import ssl

import paho.mqtt.client as mqtt


AWS_HOST  = "a2jbwrz4hgj7v1-ats.iot.ap-northeast-1.amazonaws.com"
AWS_PORT  = 8883
CA_PATH   = "./aws_iot/root-CA.crt"
CERT_PATH = "./aws_iot/iotomato.cert.pem"
KEY_PATH  = "./aws_iot/iotomato.private.key"
MAIN_TOPIC = "iotomato"
MAIN_TOPIC = "test"

MQTT_BROKER_ADDR = 'localhost'
MQTT_BROKER_PORT = 1883


def onConnect(client, userdata, flags, response_code):
    #client.subscribe("iotomato/vinyl_house", qos=0)
    client.subscribe("#", qos=0)


def onMessage(client, userdata, msg):
    if msg.topic == "iotomato/vinyl_house":
        data_str = msg.payload.decode('utf-8')
        data_dit = ast.literal_eval(data_str)
        payload_dit = {'timestamp': data_dit['timestamp']}
        payload_dit.update(data_dit['vinyl_house'])

        mqttc.publish(MAIN_TOPIC, json.dumps(payload_dit), qos=0)


if __name__ == '__main__':
    mqttc = mqtt.Client()
    mqttc.tls_set(CA_PATH, certfile=CERT_PATH, keyfile=KEY_PATH, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
    mqttc.connect(AWS_HOST, AWS_PORT, keepalive=60)

    client = mqtt.Client(protocol=mqtt.MQTTv31)
    client.on_connect = onConnect
    client.on_message = onMessage
    client.connect(host=MQTT_BROKER_ADDR, port=MQTT_BROKER_PORT, keepalive=60)
    
    try:
        client.loop_forever()
    except Error as e:
        print(e)
        pass

