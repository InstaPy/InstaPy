import requests
import json

def get_proxy():
    proxy = None
    attempts = 10
    while proxy == None and attempts > 0:
        attempts -= 1
        try:
            url = 'https://gimmeproxy.com/api/getProxy?country=US&user-agent=true&protocol=http'
            r = requests.get(url)
            proxy = json.loads(r.text)
            if 'ip' in proxy and 'port' in proxy:
                proxy['port'] = int(proxy['port'])
                return proxy
            else:
                proxy = None
        except:
            print('Trying to get proxy')

    return proxy