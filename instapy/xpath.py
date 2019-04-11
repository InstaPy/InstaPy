import json
import os
def read_xpath(function_name, xpath_name):
    fn = os.path.join(os.path.dirname(__file__), 'xpath.json')
    with open(fn) as json_file:
        xpath = json.load(json_file)
        for p in xpath[function_name]:
            xpath_val = p[xpath_name]
        return xpath_val