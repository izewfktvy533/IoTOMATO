#!/usr/bin/env python3
import ast
from datetime import datetime
import json
import time

import paho.mqtt.client as mqtt
import MySQLdb


MQTT_BROKER_ADDR = '172.29.156.52'
MQTT_BROKER_PORT = 1883
TOPIC = 'iotomato/soil_status'
HOST = "localhost"
USER = "iotomato"
PASSWD = "iotomato"
DB = "iotomato"


def onConnect(mqtt_sub, user_data, flags, response_code):
    mqtt_sub.subscribe(TOPIC, qos=0)


def onMessage(mqtt_sub, user_data, msg):
    db = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DB)
    cur = db.cursor()

    payload_dit  = ast.literal_eval(msg.payload.decode('utf-8'))
    table_name = msg.topic.split('/')[1]
    timestamp        = payload_dit['timestamp']
    temperature      = payload_dit['TEMP']
    vwc              = payload_dit['VWC']
    ec               = payload_dit['EC']

    query = "insert into {0} (timestamp, temperature, vwc, ec) values (%s, %s, %s, %s)".format(table_name)
    ret = cur.execute(query, (timestamp, temperature, vwc, ec))

    while not ret == 1:
        ret = cur.execute(query)
        time.sleep(0.001)

    db.commit()
    cur.close()
    db.close()


mqtt_sub = mqtt.Client(protocol=mqtt.MQTTv31)
mqtt_sub.on_connect = onConnect
mqtt_sub.on_message = onMessage
mqtt_sub.connect(host=MQTT_BROKER_ADDR, port=MQTT_BROKER_PORT, keepalive=60)


try:
    mqtt_sub.loop_forever()

except KeyboardInterrupt:
    mqtt_sub.disconnect()
    exit(0)

