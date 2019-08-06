import paho.mqtt.client as mqtt
from random import uniform
from time import sleep


MQTT_BROKER_ADDR = '172.29.156.83'
MQTT_BROKER_PORT = 1883

mqtt_client = mqtt.Client(protocol=mqtt.MQTTv31)
mqtt_client.connect(host=MQTT_BROKER_ADDR, port=MQTT_BROKER_PORT, keepalive=0)



try:
	mqtt_client.publish("SmartInoueLab/gateway/air_conditioner", "{'power':'on'}", qos=0)
	sleep(3)
	mqtt_client.publish("SmartInoueLab/gateway/air_conditioner", "{'power':'off'}", qos=0)

except KeyboardInterrupt:
	None
