import paho.mqtt.client as mqtt


MQTT_BROKER_ADDR = '172.29.156.91'
MQTT_BROKER_PORT = 1883


def onConnect(client, userdata, flags, response_code):
    print(userdata)
    client.subscribe("#", qos=0)


def onMessage(client, userdata, msg):
    print(userdata)
    print("topic  : " + msg.topic)
    print("payload: " + str(msg.payload))
    print()


client = mqtt.Client(userdata="test", protocol=mqtt.MQTTv31)
client.on_connect = onConnect
client.on_message = onMessage
client.connect(host=MQTT_BROKER_ADDR, port=MQTT_BROKER_PORT, keepalive=0)

try:
    client.loop_forever()
except KeyboardInterrupt:
    None
