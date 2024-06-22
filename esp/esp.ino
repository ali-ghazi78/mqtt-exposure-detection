#include <WiFi.h>
#include <HTTPClient.h>
#include <PubSubClient.h>
#define SECOND 1000UL


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

const char * topic_mac= "MAC_ADDRESS";
const char * topic_expose_status= "expose_status";
  

enum DebugLevel{
    NoVerbose,
    Verbose,
    VeryVerbose,
    
}debug_level;

int DEBUG_LEVEL=NoVerbose;

void connect_to_wifi()
{
    delay(1000);

    WiFi.mode(WIFI_STA); //Optional
    WiFi.begin(ssid, password);
    Serial.println("\nConnecting");

    while(WiFi.status() != WL_CONNECTED)
    {    
    Serial.print(".");
    if (DEBUG_LEVEL==VeryVerbose)
        Serial.print(WiFi.status());
    delay(1000);
    }

    Serial.println("\nConnected to the WiFi network");
    Serial.print("Local ESP32 IP: ");
    Serial.println(WiFi.localIP());
}
enum codes_enum {
    NO_WIFI=-10,
    HTTP_ERROR=-11,
    RESULT_FOUND=-1111,
    
}error_code;

class ResultDict{
    public:
        String found="False";
        int success_http_request=0; //0 means http is successful. 1 means there was an error
        String search_engine_name="";
};



HTTPClient http;
class SearchEngine{
    public: 
        String engine_name;
        String search_term ; 
        String server_path;
        String not_found_result_str;
        String place_holder="PLACEHOLDER";
        ResultDict result_dict;

        SearchEngine(String engine_name){
            this->engine_name = engine_name;
            this->result_dict.search_engine_name = engine_name;
        }

        ResultDict get_result_from_search_engine()
        {
            String engine_url = this->get_url();
            int result_temp = send_http_request_and_does_query_exist(engine_url, this->not_found_result_str);
            if (result_temp == RESULT_FOUND){
                this->result_dict.found = "True";
            }
            else{
                this->result_dict.found = "False";
            }
            if (result_temp == HTTP_ERROR || result_temp == HTTP_ERROR){
                this->result_dict.success_http_request = 1;
            }
            else{
                this->result_dict.success_http_request = 0;
            }
            return this->result_dict;
        }

    private:
        String get_url()
        {
            return this->server_path + this->replace_place_holder_with_mac_address();
        }
        String replace_place_holder_with_mac_address()
        {
            String temps = search_term;
            temps.replace(this->place_holder, MY_MAC_ADDRESS);
            String new_search_term = temps;
            return new_search_term;
        }
        int send_http_request_and_does_query_exist(String url, String not_found_result_str)
        {
            if(WiFi.status()!= WL_CONNECTED)
                return NO_WIFI;

            if (DEBUG_LEVEL>=Verbose)
                Serial.println("url:" + url);

            http.begin(url.c_str());
            http.addHeader("User-Agent", "Mozilla/5.0");

            int httpResponseCode = http.GET();
            int indexOfsearchTerm = HTTP_ERROR;
            if (httpResponseCode>0) 
            {
                if (DEBUG_LEVEL>=Verbose)
                    Serial.print("HTTP Response code: " + httpResponseCode);

                String payload = http.getString();
                if (payload.indexOf("Too Many Requests")!=-1){
                    return HTTP_ERROR;
                }
                indexOfsearchTerm = payload.indexOf(not_found_result_str);
                if (indexOfsearchTerm == -1)
                    indexOfsearchTerm = RESULT_FOUND;
                if (DEBUG_LEVEL==VeryVerbose)
                    Serial.println(payload);
                if (DEBUG_LEVEL>=Verbose){
                    Serial.println("did we find the string? (-1111 means we found results.)");
                    Serial.println(indexOfsearchTerm);
                }
            }
            else 
            {
                Serial.print("Error code: ");
                Serial.println(httpResponseCode);
                return HTTP_ERROR;
            }
            http.end();
            return indexOfsearchTerm;

        }
};


int len_search_engines = 2;
SearchEngine shodan("shodan");
SearchEngine zoomeye("zoomeye");
ResultDict engine_list[2];
ResultDict shodan_result;
ResultDict zoomeye_result;




String Get_aggregated_result_from_search_engines(){
    shodan_result  = shodan.get_result_from_search_engine();
    zoomeye_result = zoomeye.get_result_from_search_engine();
    engine_list[0] = shodan_result;
    engine_list[1] = zoomeye_result;

    String aggregated_str = "[(time,"+ String(MY_MAC_ADDRESS) +"),";
    for(int i=0;i<len_search_engines;i++){
        aggregated_str += "(\'" + engine_list[i].search_engine_name +"\',"+ String(engine_list[i].found)+","+String(engine_list[i].success_http_request) + "),";
    }
    aggregated_str = aggregated_str + "]"; 
    return aggregated_str;
}  



WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
    Serial.begin(115200);
    Serial.println("Hello");  
    connect_to_wifi();

    client.setServer(mqtt_broker, mqtt_port);
    
    while (!client.connected()) {
        String client_id = "esp32-client-";
        client_id += String(WiFi.macAddress());
        Serial.printf("The client %s connects to the public MQTT broker\n", client_id.c_str());
        if(authentication_required && client.connect(client_id.c_str(), broker_username, broker_password))
            Serial.println("Public MQTT broker connected");
        else if (!authentication_required && client.connect(client_id.c_str())) {
            Serial.println("Public MQTT broker connected");
        } else {
            Serial.print("failed with state ");
            Serial.print(client.state());
            delay(2000);
        }
    }






    // ======================================== set up search engines in here ========================================
    shodan.server_path="https://www.shodan.io";
    shodan.place_holder = "PLACEHOLDER";
    shodan.search_term = "/search?query=PLACEHOLDER";
    shodan.not_found_result_str = "No results found";

    zoomeye.server_path="https://www.zoomeye.hk";
    zoomeye.place_holder = "PLACEHOLDER";
    zoomeye.search_term = "/api/aggs?q=PLACEHOLDER&l=en&t=v4%2Bv6%2Bweb";
    zoomeye.not_found_result_str = "\"country\": []";
    // ========================================


}

void loop() {

    while (!client.connected()) {
        String client_id = "esp32-client-";
        client_id += String(WiFi.macAddress());
        Serial.printf("The client %s connects to the public MQTT broker\n", client_id.c_str());
        if(authentication_required && client.connect(client_id.c_str(), broker_username, broker_password))
            Serial.println("Public  MQTT broker connected");
        else if (!authentication_required && client.connect(client_id.c_str())) {
            Serial.println("Public  MQTT broker connected");
        } else {
            Serial.print("failed with state ");
            Serial.print(client.state());
            delay(2000);
        }
    }

    // String aggregated_str = "Get_aggregated_result_from_search_engines()";


    String aggregated_str = Get_aggregated_result_from_search_engines();
    client.publish(topic_mac, MY_MAC_ADDRESS);
    client.publish(topic_expose_status, aggregated_str.c_str());

    Serial.println(aggregated_str);
    delay(SECOND*check_interval);
}
