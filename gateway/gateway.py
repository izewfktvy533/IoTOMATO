from xbee import ZigBee
import paho.mqtt.client as mqtt
import serial
import sys
import time
import threading
from datetime import datetime
import os
import json
import ast


PORT = '/dev/ttyUSB0'
BAND_RATE = 9600
SERIAL_PORT = serial.Serial(PORT, BAND_RATE)
MQTT_BROKER_ADDR = '172.29.156.95'
MQTT_BROKER_PORT = 1883
MAIN_TOPIC = "inouelab/sensing_part/"
DIRECTORY_NAME = "/home/pi/WorkSpace/IoTOMATO/gateway/data/sensing_part/"



def handleXBee(xbee_packet):
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
        
        #thread_send_mqtt_broker = threading.Thread(target=send_mqtt_broker, args=(sub_topic_str, payload_dit))
        thread_store_data = threading.Thread(target=store_data, args=(directory_name_str, file_name_str, payload_dit))

        mqtt_packet = json.dumps(payload_dit)
        mqtt_client.publish(MAIN_TOPIC + sub_topic_str, mqtt_packet, qos=0)

        cpath = os.path.abspath("./")

        try:
            os.chdir(sub_topic_str)
        
        except FileNotFoundError:
            os.mkdir(sub_topic_str)
            os.chdri(sub_topic_str)

        with open(file_name_str, 'a') as fp:
            json.dump(payload_dit, fp)
            fp.write("\n")
        
        os.chdir(cpath)

    except UnicodeDecodeError: 
        None

    except ValueError:
        None


if __name__ == '__main__':
    os.chdir(DIRECTORY_NAME)
    xbee = ZigBee(SERIAL_PORT, escaped=True, callback=handleXBee)
    mqtt_client = mqtt.Client(protocol=mqtt.MQTTv31)
    mqtt_client.connect(host=MQTT_BROKER_ADDR, port=MQTT_BROKER_PORT, keepalive=0)

    try:
        while True:
            time.sleep(0.000001)

    except KeyboardInterrupt:
        #mqtt_client.disconnect()
        xbee.halt()
        SERIAL_PORT.close()
        sys.exit(1)
