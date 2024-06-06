import datetime
from urllib.request import Request, urlopen
import uuid
import config
# https://www.criminalip.io/en
# https://search.censys.io/
# https://www.onyphe.io/

DEBUG = False

place_holder = "PLACEHOLDER"
shodan_search_engine_dict = {
    "engine_name": "shodan",
    "webaddress":"https://www.shodan.io",
    "key_query": f"/search?query={place_holder}",
    "not_found_result_str": "No results found",
    "header":{'User-Agent': 'Mozilla/5.0',}
}

zoomeye_search_engine_dict = {
    "engine_name": "zoomeye",
    "webaddress":"https://www.zoomeye.hk",
    "key_query": f"/api/aggs?q={place_holder}&l=en&t=v4%2Bv6%2Bweb",
    "not_found_result_str": "\"country\": []",
    "header":{'User-Agent': 'Mozilla/5.0',}

}

search_engines_list = [shodan_search_engine_dict, 
                      zoomeye_search_engine_dict
                      ]



class searchengine:
    def __init__(self, search_engine_dict,mac_based_str, place_holder="PLACEHOLDER" ):
        self.webaddress = search_engine_dict["webaddress"]
        self.key_query = search_engine_dict["key_query"]
        self.not_found_result_str = search_engine_dict["not_found_result_str"]
        self.engine_header = search_engine_dict["header"]
        self.place_holder = place_holder
        self.set_mac_based_query(mac_based_str)
        self.error_str = "An error occured fetching search engine!"
        self.success_code = 0
        self.failed_code = 1
        
    def does_query_exist(self):
        webpage = str(self.get_html_response())
        if self.error_str in webpage:
            return False, self.failed_code
        
        if self.not_found_result_str in webpage:
            return False, self.success_code
        else:
            return True, self.success_code
        
    def get_html_response(self):
        url = self.webaddress + self.key_query
        if DEBUG:
            print(f"url request is:{url}",flush=True)
        try:
            req = Request(
                url=url, 
                headers=self.engine_header.copy()
            )
            self.webpage = urlopen(req)        
        
        except Exception as e:
            if DEBUG:
                print(f"{self.error_str}: {e}")
            return str(f"{self.error_str}: {e}")

        code = self.webpage.getcode()
        self.webpage = self.webpage.read()
        if DEBUG:
            print(f"response code is:{code}",flush=True)
        return str(self.webpage)



    def set_mac_based_query(self, mac_based_query_str):
        self.key_query = self.key_query.replace(self.place_holder,  mac_based_query_str)


def is_any_records_on_search_engines(search_engines_list, mac_based_str="gps"):
    dt = datetime.datetime.now(datetime.timezone.utc) 
    dt = str(dt)
    
    found_list = [(dt,mac_based_str)]
    for se in search_engines_list:
        if DEBUG:
            print(f"trying: {se['engine_name']}",flush=True)
        engine = searchengine(se, mac_based_str=mac_based_str)
        r = engine.get_html_response()
        r, success_code = engine.does_query_exist()
        if DEBUG:
            print(f"any result on {se['engine_name']}? {r}, success code:{str(success_code)}",flush=True)
        found_list.append((se['engine_name'], r, success_code))
    return found_list


if __name__ =="__main__":
    found_list = is_any_records_on_search_engines(search_engines_list=search_engines_list, mac_based_str="gps")
    print(found_list,flush=True)







# def get_mac():
#   mac_num = hex(uuid.getnode()).replace('0x', '').upper()
#   mac = ''.join(mac_num[i: i + 2] for i in range(0, 11, 2))
#   return mac
