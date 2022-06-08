import paho.mqtt.client as mqtt
import influx

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    topicNames = ["temperature", "humidity", "gas", "aqi", "wifi" ]
    topics = [(f"hjsensor/+/+/{top}", 0) for top in topicNames]
    print(topics)
    client.subscribe(topics)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    topic_split = msg.topic.split("/")
    field = topic_split[-1]
    gps = topic_split[2]
    id = topic_split[1]
    value = msg.payload.decode("utf-8")

    influx.InfluxClient(id, gps, field, float(value))
    #print("MQTT to InfluxDB")
    

client = mqtt.Client("client123")
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set("iot2020", "mqtt2020*")

client.connect("130.136.2.70", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()