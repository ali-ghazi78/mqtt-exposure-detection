# What is this repo? 
This repository searches on search engines like shodan and zoomeye to check if your MQTT server is exposed or not 

# How does it work
We create a publisher client that publishes the MAC address of your pc to the broker. In case shodan or other search engines connect to the broker, they will get the information of the topics that are sent to the broker. Now, since we are publishing a topic with our MAC address, shodan will save our MAC address in its results. Therefore, if we search our MAC address on shodan we will get the records related to our system.

# implementations
We have 3 different implementations
1. [docker based client](#docker-based-agent) 
2. [ESP32 based](#esp32-agent)
3. [docker based client embedded in an EQMX docker-compose](#agent-within-broker)


# docker based agent
Our system consists of two parts:

1. [MAC publisher](#MAC_publisher)
2. [search_engine_crawler](#search_engine_crawler)

### 1. MAC publisher <a id='MAC_publisher'></a>
We created a script that sends the followin topic to the broker
```
MAC_ADDRESS/
```
for instance
```
C8215D576D60
```
(please note the MAC address should not contain any dash sign.) 

and its contents is the UTC time. 

### 2. search engine crawler<a id='search_engine_crawler'></a>
In this part, the agent searchs for the MAC address on shodan and zoomeye to check if it can find any results or not and it will send the receieved information to the MQTT broker through the following topic
```
expose_status
```
and the message content is like the following
```
 [('2024-06-06 22:34:42.803736+00:00', 'C8215D576D60'), ('shodan', False, 0), ('zoomeye', False, 0)]
```
The first cell of the message contains the UTC time(2024-06-06 22:34:42.803736+00:00) of the search and the keyword(mac address C8215D576D60) that was searched. The rest of the cells contain the information of search reult. The first string is the name of search engine such as 'shodan' or 'zoomeye'. The True or False boolean in the following cell states if any results have been find or not. The next value is a 0 or 1 which is the error code. if the error code is 0 it means that the agent has successfully connected to the mentioned engines and MQTT broker, however, if the error code is 1 it means that there has been an error either connecting the MQTT server or querying the search engines. 


## Running the docker file
first edit the config file as needed.

### config file
there is a config file located in the 
```
/docker_base/src
```
The contents of the config is as followows 
please note that you **_must put the MAC address in the config file manually_** since docker cannot get your real MAC address.  

```

mac_address = 'C8215D576D60' #without dash(-) sign 
broker_ip = "192.168.56.1"
broker_port = 1883
broker_username = ""
broker_password = ""
authentication_required = False
publish_mac_interval = 3600 #in seconds 
publish_mac_interval_if_network_error = 10 #in seconds
Search_engine_check_interval = 20 # in seconds
```
second, go to the ```/docker_based``` folder and run the following command 
```
docker-compose up --build -d 
```


# ESP32 Agent
since some IoT systems do not have any PC involved and the broker is run on an ESP32 microcontroller, we implemented the same functionallity for the ESP32 as well. 
First you need to go to the ```esp``` folder and then upload the code unsing arduino enviornment to the ESP32 device. For this project we used an ```ESP32_DEVKITC_V4```.
Please note that you must setup the configurations in the begineing of the code. You must obtain and put your mac address in the MY_MAC_ADDRESS field. please note that for the ESP32 code, we do not send the time to the broker since accurate timing needs NTP server which some IoT systems might not have this option available. 
```
////================================= configuration ==============================
// MAC ADDRESS
const char * MY_MAC_ADDRESS  = "C8215D576D60";


// WiFi
const char* ssid = "Mywifi";
const char* password = "mypassword";

// MQTT Broker
const char *mqtt_broker = "192.168.1.90";
const char *broker_username  = "";
const char *broker_password  = "";
const int mqtt_port = 1883;
bool authentication_required = false;
int check_interval=10; // in seconds 

////================================= configuration ==============================
```
The output format of the ESP32 agent is just like the output format of the previous part.

# Agent within broker
In case you want to have this exposure detection system along your MQTT broker, we also prepared a docker-compose file that runs the MQTT server and our code in a single docker-compose file for ease of use. Please note that you still need to set the IP address and other configurations in the config file for the exposure detection code.
To use this code you need to firt go to the ```/docker_based``` folder and then run the following command
```
docker-compose -f  docker-compose-with-broker.yml up --build
```

