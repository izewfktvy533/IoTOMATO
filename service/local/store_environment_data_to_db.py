#!/usr/bin/env python3
import ast
from datetime import datetime
import json
import time

import paho.mqtt.client as mqtt
import MySQLdb


MQTT_BROKER_ADDR = '172.29.156.52'
MQTT_BROKER_PORT = 1883
TOPIC = 'iotomato/device/environment/#'
HOST = "localhost"
USER = "iotomato"
PASSWD = "iotomato"
DB = "iotomato"


def onConnect(mqtt_sub, user_data, flags, response_code):
    mqtt_sub.subscribe(TOPIC, qos=0)


def onMessage(mqtt_sub, user_data, msg):
    db = MySQLdb.connect(host=HOST, user=USER, passwd=PASSWD, db=DB)
    cur = db.cursor()
    payload_dit = ast.literal_eval(msg.payload.decode('utf-8'))
    timestamp = payload_dit['timestamp']
    target = msg.topic.split('/')[2]
    device_id = msg.topic.split('/')[4]

    try:
        temperature = payload_dit['temperature']
    except KeyError:
        temperature = None

    try:
        humidity = payload_dit['humidity']
    except KeyError:
        humidity = None

    try:
        pressure = payload_dit['pressure']
    except KeyError:
        pressure = None

    try:
        light = payload_dit['light']
    except KeyError:
        light = None
    
    try:
        co2 = payload_dit['co2']
    except KeyError:
        co2 = None
    
    try:
        water_level = payload_dit['water_level']
    except KeyError:
        water_level = None
    
    query = "insert into {} (device_id, timestamp, temperature, humidity, pressure, light, co2, water_level) values (%s, %s, %s, %s, %s, %s, %s, %s)".format(target)
    values = (device_id, timestamp, temperature, humidity, pressure, light, co2, water_level)
    ret = cur.execute(query, values)

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

