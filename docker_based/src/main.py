import datetime
from check_search_engines import * 
import threading, time
import paho.mqtt.client as mqtt



def publish_expose_status(topic, message):
    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")
        # client.subscribe("$SYS/#")
    def on_message(client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))

    broker_ip       = config.broker_ip
    broker_port     = config.broker_port
    broker_password = config.broker_password
    broker_username = config.broker_username

    try:
        mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message
        if config.authentication_required:
            mqttc.username_pw_set(username=broker_username,password=broker_password)
        mqttc.connect(host=broker_ip, port=broker_port, keepalive=60)
        mqttc.loop_start()

        mqttc.publish(topic,message, retain=True)
        print("published msg:", topic, message, flush=True)
        mqttc.disconnect()
        mqttc.loop_stop()
        return f"sent {topic}/{message}"
        
    except Exception as e:
        print("error in publishing: ", e,flush=True)
        time.sleep(config.publish_mac_interval_if_network_error) # every 1 hour
        return "error occured"

def periodic_func(mac_based_str):
    try:
        found_list = is_any_records_on_search_engines(search_engines_list=search_engines_list, mac_based_str=mac_based_str)
        return found_list
    except Exception as e:
        print(e,flush=True)
        return "error"

while True:
    try:
        WAIT_TIME_SECONDS = config.Search_engine_check_interval
        ticker = threading.Event()
        while not ticker.wait(WAIT_TIME_SECONDS):
            found_list = periodic_func(mac_based_str=config.mac_address)
            print(found_list,flush=True)
            publish_expose_status("expose_status",str(found_list))

    except Exception as e:
        print(e,flush=True)




