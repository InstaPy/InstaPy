from .xpath_compile import xpath
from .time_util import new_seed



def read_xpath(function_name, xpath_name):
    # new seed each time this function is called
    new_seed()
    
    return xpath[function_name][xpath_name]
