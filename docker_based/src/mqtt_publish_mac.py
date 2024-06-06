import random
import paho.mqtt.client as mqtt
import time
from datetime import datetime,timezone
from datetime import timezone 
import datetime 
import uuid
import config


print("====================== MAC Publisher script ====================== ",flush=True)



def get_mac():
#   mac_num = hex(uuid.getnode()).replace('0x', '').upper()
#   mac = ''.join(mac_num[i: i + 2] for i in range(0, 11, 2))
  mac = config.mac_address
  return mac

def get_utc_time_now():
    dt = datetime.datetime.now(timezone.utc) 
    
    utc_time = dt.replace(tzinfo=timezone.utc) 
    utc_timestamp = utc_time.timestamp() 
    return utc_timestamp

def create_mac_based_topic():
    utc_time = get_utc_time_now()
    topic_name = get_mac()
    mac_based_topic_name = topic_name + "/" + str(utc_time)
    return mac_based_topic_name



mac_and_utc_based_topic = create_mac_based_topic()



def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # client.subscribe("$SYS/#")
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


broker_ip       = config.broker_ip
broker_port     = config.broker_port
broker_password = config.broker_password
broker_username = config.broker_username

while True:
    try:
        mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message
        if config.authentication_required:
            mqttc.username_pw_set(username=broker_username,password=broker_password)
        mqttc.connect(host=broker_ip, port=broker_port, keepalive=60)
        mqttc.loop_start()

        while True:
            mqttc.publish(get_mac(), str(get_utc_time_now()), retain=True)
            print(str(get_utc_time_now()),flush=True)
            # mqttc.publish(mac_and_utc_based_topic, random_value, retain=False) # avoiding too many retained messages
            time.sleep(config.publish_mac_interval) # every 1 hour

    except Exception as e:
        print("error in publishing: ", e,flush=True)
        time.sleep(config.publish_mac_interval_if_network_error) # every 1 hour


# mqttc.loop_stop()
