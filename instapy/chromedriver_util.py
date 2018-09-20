import os
from .settings import Settings

def driver_update(desired_version=[]):
    # constants
    CHROME_DL_URL = 'https://chromedriver.storage.googleapis.com'
    CHROME_URL = 'http://chromedriver.chromium.org/downloads'
    VERSION_FILE = os.path.join(Settings.assets_location, 'version.txt')
    DOWNLOAD_DIR = Settings.assets_location
    CURRENT_VERSION = [] 
    DESIRED_VERSION = []
    
    if not desired_version == "latest":
        DESIRED_VERSION = desired_version

    # chromedriver versions for downloading only
    DRIVER = 'chromedriver_'
    ZIP = '.zip'
    vMAC = DRIVER + 'mac64' + ZIP
    vWINDOWS = DRIVER + 'win32' + ZIP
    vLINUX = DRIVER + 'linux64' + ZIP
    PLATFORMS = [ vMAC, vLINUX, vWINDOWS ]

    if not CURRENT_VERSION:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE) as f:
                CURRENT_VERSION = f.read().strip().split('.')
        else:
            CURRENT_VERSION = [0, 0]

    if not DESIRED_VERSION:
        import requests
        from bs4 import BeautifulSoup as bs
        import urllib
        import platform

        page = requests.get(CHROME_URL)
        html = page.content

        soup = bs(html, 'html.parser')

        latest = soup.find(id='sites-canvas-main-content').table.tbody.tr.td.div.find_all('h2')[1].b.a

        new_version = latest.text.split(' ')[1].split('.')
    else:
        new_version = DESIRED_VERSION

    # update logic
    length = len(new_version)
    if len(CURRENT_VERSION) < length:
        length = len(CURRENT_VERSION)

    update = False
    for i in range(length):
        new = int(new_version[i])
        old = int(CURRENT_VERSION[i])

        if new > old:
            update = True
            break

    if update:
        sys = platform.system()
        
        # choose the correct version
        pf = vWINDOWS
        if sys == "Darwin":
            pf = vMAC
        elif sys == "Linux":
            pf = vLINUX

        url = CHROME_DL_URL + '/' + '.'.join(new_version) + '/' + pf
        print(url)

        #downloads the files
        file = urllib.request.urlopen(url)
        path = os.path.join(DOWNLOAD_DIR, pf)

        with open(path,'wb') as output:
            output.write(file.read())

        #unzip file
        import zipfile
        with zipfile.ZipFile(path,"r") as zip_ref:
            zip_ref.extractall(DOWNLOAD_DIR)

        #delete zip file
        os.remove(path)

        # write version file
        with open(VERSION_FILE, "wb") as vFile:
            f.write('.'.join(new_version))

