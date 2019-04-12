from .xpath_compile import xpath

def read_xpath(function_name, xpath_name):
    for p in xpath[function_name]:
        xpath_val = p[xpath_name]
    return xpath_val
