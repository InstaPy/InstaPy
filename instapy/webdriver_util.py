import os
from .settings import Settings
import platform
import urllib

# constants
DOWNLOAD_DIR = Settings.assets_location
VERSION_FILE = os.path.join(Settings.assets_location, 'version.txt')


def driver_update(desired_version="", logger=None):
    current_version = []
    DESIRED_VERSION = []

    if not desired_version == "latest":
        DESIRED_VERSION = str(desired_version).split('.')

    if not current_version:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE) as f:
                file_content = f.read()
                if file_content:
                    current_version = file_content.strip().split('.')
                else:
                    current_version = ["0", "0"]
        else:
            current_version = ["0", "0"]

    logger.info("Current Webdriver Version: " + ".".join(current_version))

    update = False

    if not DESIRED_VERSION:
        new_version = get_latest_version(logger)
        # update logic
        length = len(new_version)
        if len(current_version) < length:
            length = len(current_version)

        for i in range(length):
            new = int(new_version[i])
            old = int(current_version[i])

            if new > old:
                update = True
                break
    else:
        new_version = DESIRED_VERSION
        # always updates if current version is not desired version
        if not current_version == new_version:
            update = True

    logger.info("Desired Webdriver Version: " + ".".join(new_version))

    if update:
        update_webdriver(new_version, logger)


def update_webdriver(version, logger):
    logger.info("Updating Driver...")
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
    logger.info("Start downloading: " + url)

    # downloads the files
    file = urllib.request.urlopen(url)
    path = os.path.join(DOWNLOAD_DIR, pf)

    with open(path, 'wb') as output:
        output.write(file.read())

    logger.info("Finished downloading file to: " + path)

    # unzip file
    import zipfile
    with zipfile.ZipFile(path, "r") as zip_ref:
        zip_ref.extractall(DOWNLOAD_DIR)

    logger.info("Unzipped File.")

    # delete zip file
    os.remove(path)
    logger.info("Deleted Zip archive.")

    # write version file
    with open(VERSION_FILE, "w") as vFile:
        vFile.write('.'.join(version))


def get_latest_version(logger):
    CHROME_URL = 'http://chromedriver.chromium.org/downloads'

    import requests
    from bs4 import BeautifulSoup as bs

    page = requests.get(CHROME_URL)
    html = page.content

    soup = bs(html, 'html.parser')

    latest = soup.find(
        id='sites-canvas-main-content').table.tbody.tr.td.div.find_all('h2')[1].b.a

    new_version = latest.text.split(' ')[1].split('.')
    logger.info("Lates Version available is: " + ".".join(new_version))

    return new_version
