import os
from .settings import Settings
import platform
import urllib

# constants
DOWNLOAD_DIR = Settings.assets_location
VERSION_FILE = os.path.join(Settings.assets_location, 'version.txt')


def driver_update(desired_version=[]):
    current_version = []
    DESIRED_VERSION = []

    if not desired_version == "latest":
        DESIRED_VERSION = desired_version

    if not current_version:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE) as f:
                current_version = f.read().strip().split('.')
        else:
            current_version = [0, 0]

    if not DESIRED_VERSION:
        new_version = get_latest_version()
    else:
        new_version = DESIRED_VERSION

    # update logic
    length = len(new_version)
    if len(current_version) < length:
        length = len(current_version)

    update = False
    for i in range(length):
        new = int(new_version[i])
        old = int(current_version[i])

        if new > old:
            update = True
            break

    if update:
        update_webdriver(new_version)


def update_webdriver(version):
    CHROME_DL_URL = 'https://chromedriver.storage.googleapis.com'

    # chromedriver versions for downloading only
    DRIVER = 'chromedriver_'
    ZIP = '.zip'
    vMAC = DRIVER + 'mac64' + ZIP
    vWINDOWS = DRIVER + 'win32' + ZIP
    vLINUX = DRIVER + 'linux64' + ZIP

    sys = platform.system()

    # choose the correct version
    pf = vWINDOWS
    if sys == "Darwin":
        pf = vMAC
    elif sys == "Linux":
        pf = vLINUX

    url = CHROME_DL_URL + '/' + '.'.join(version) + '/' + pf

    # downloads the files
    file = urllib.request.urlopen(url)
    path = os.path.join(DOWNLOAD_DIR, pf)

    with open(path, 'wb') as output:
        output.write(file.read())

    # unzip file
    import zipfile
    with zipfile.ZipFile(path, "r") as zip_ref:
        zip_ref.extractall(DOWNLOAD_DIR)

    # delete zip file
    os.remove(path)

    # write version file
    with open(VERSION_FILE, "w") as vFile:
        vFile.write('.'.join(version))


def get_latest_version():
    CHROME_URL = 'http://chromedriver.chromium.org/downloads'

    import requests
    from bs4 import BeautifulSoup as bs

    page = requests.get(CHROME_URL)
    html = page.content

    soup = bs(html, 'html.parser')

    latest = soup.find(
        id='sites-canvas-main-content').table.tbody.tr.td.div.find_all('h2')[1].b.a

    new_version = latest.text.split(' ')[1].split('.')

    return new_version
