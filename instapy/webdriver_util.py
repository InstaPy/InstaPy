import os
import zipfile
import platform
import urllib
import requests
from bs4 import BeautifulSoup as bs
from .settings import Settings

# constants
DOWNLOAD_DIR = Settings.assets_location
VERSION_FILE = os.path.join(Settings.assets_location, 'version.txt')


def driver_update(desired_version="", logger=None):
    current_version = []
    latest = True

    if not desired_version == "latest":
        desired_version = str(desired_version).split('.')
        latest = False

    if not current_version:
        if os.path.exists(VERSION_FILE):
            with open(VERSION_FILE) as file:
                file_content = file.read()
                if file_content:
                    current_version = file_content.strip().split('.')
                else:
                    current_version = ["0", "0"]
        else:
            current_version = ["0", "0"]

    if current_version == ["0", "0"]:
        logger.info("No versioned webdriver found.")
    else:
        logger.info("Current webdriver version: " + ".".join(current_version))

    update = False

    if latest:
        new_version = get_latest_chromedriver_version(logger)

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
        new_version = desired_version
        # always updates if current version is not desired version
        if not current_version == new_version:
            update = True

    logger.info("Desired webdriver version: " + ".".join(new_version))

    if update:
        download_chromedriver(new_version, logger)


def download_chromedriver(version, logger):
    logger.info("Updating driver...")
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

    logger.info("Finished downloading file: " + path)

    # unzip file
    with zipfile.ZipFile(path, "r") as zip_ref:
        zip_ref.extractall(DOWNLOAD_DIR)

    logger.info("Unzipped webdriver.")

    # delete zip file
    os.remove(path)
    logger.info("Deleted zip archive.")

    # write version file
    with open(VERSION_FILE, "w") as vFile:
        vFile.write('.'.join(version))

    logger.info("Finished updating webdriver.")


def get_latest_chromedriver_version(logger):
    CHROME_URL = 'http://chromedriver.chromium.org/downloads'

    page = requests.get(CHROME_URL)
    html = page.content

    soup = bs(html, 'html.parser')

    latest = soup.find(
        id='sites-canvas-main-content').table.tbody.tr.td.div.find_all('h2')[1].b.a

    new_version = latest.text.split(' ')[1].split('.')
    logger.info("Latest version available is: " + ".".join(new_version))

    return new_version
