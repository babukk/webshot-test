#! /usr/bin/env python
# -------------------------------------------------------------------------------------------------------------------------------------------------------

import uuid
import time
import optparse
import json
import urllib.request
import ssl
import os
import logging

from selenium import webdriver
from pyvirtualdisplay import Display
from PIL import Image


SAVE_PATH = "shots"
DRIVERS = ["firefox", "phantom"]
DRIVER = "phantom"
WAIT_INTERVAL = 2
URL = None
BROWSER = None
IMAGE_QUALITY = 60

# -------------------------------------------------------------------------------------------------------------------------------------------------------
def init():
    global URL, DRIVER, DRIVERS, WAIT_INTERVAL, SAVE_PATH, IMAGE_QUALITY
    parser = optparse.OptionParser(usage=" ")

    parser.add_option("-u", "--url", dest="url", metavar="http://www.google.com")
    parser.add_option("-d", "--driver", dest="driver", metavar="firefox or phantom")
    parser.add_option("-i", "--interval", dest="interval", metavar="2")
    parser.add_option("-p", "--path", dest="save_path", metavar="img")
    parser.add_option("-q", "--quality", dest="quality", metavar="90")

    (options, args) = parser.parse_args()

    if options.url is not None:
        URL = options.url
    else:
        parser.print_help()
        exit()

    if options.driver is not None:
        if options.driver in DRIVERS:
            DRIVER = options.driver
        else:
            parser.print_help()
            exit()

    if options.interval is not None:
        try:
            WAIT_INTERVAL = float(options.interval)
        except Exception as msg:
            pass

    if options.save_path is not None:
        SAVE_PATH = options.save_path

    if options.quality is not None:
        if options.quality.isdigit():
            quality = int(options.quality)
            if quality < 1:
                quality = 1

            if quality > 100:
                quality = 100

            IMAGE_QUALITY = quality

    if not os.path.exists(SAVE_PATH):
        try:
            os.makedirs(SAVE_PATH)
        except Exception as msg:
            message("error", str(msg))
            exit()

# -------------------------------------------------------------------------------------------------------------------------------------------------------
def message(status, message):
    data = {"status": status, "message": message}
    print(json.dumps(data))

# -------------------------------------------------------------------------------------------------------------------------------------------------------
def create_display():
    try:
        display = Display(visible=0, size=(1280, 1024))
        display.start()
        logging.info("Virtual Display Started")
    except:
        pass

# -------------------------------------------------------------------------------------------------------------------------------------------------------
def create_browser():
    global BROWSER

    if DRIVER == "firefox":
        try:
            BROWSER = webdriver.Firefox()
        except Exception as msg:
            message("error", str(msg))
            exit()

    if DRIVER == "phantom":
        try:
            BROWSER = webdriver.PhantomJS()
            BROWSER.set_window_size(1024, 768)
            headers = {
                'Accept':'*/*',
                'Accept-Encoding':'gzip, deflate, sdch',
                'Accept-Language':'en-US,en;q=0.8',
                'Cache-Control':'max-age=0',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
            }

            for key, value in enumerate(headers):
                capability_key = 'phantomjs.page.customHeaders.{}'.format(key)
                webdriver.DesiredCapabilities.PHANTOMJS[capability_key] = value

        except Exception as msg:
            message("error", str(msg))
            exit()

# -------------------------------------------------------------------------------------------------------------------------------------------------------
def check_url():
    global URL

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE


        req = urllib.request.Request(
            URL,
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )

        req = urllib.request.urlopen(req, context=ctx, timeout=20)

        if req.getcode() != 200:
            message("error", "url could not open")
            exit()

    except Exception as msg:
        message("error", str(msg))
        exit()

# -------------------------------------------------------------------------------------------------------------------------------------------------------
def take_screenshot():
    global URL, BROWSER, SAVE_PATH, WAIT_INTERVAL, IMAGE_QUALITY

    SAVE_FILE_TEMP = "%s/%s_tmp.png" % (SAVE_PATH, uuid.uuid1())
    SAVE_FILE = "%s/%s.jpg" % (SAVE_PATH, uuid.uuid1())

    try:
        BROWSER.get(URL)

        body = BROWSER.find_element_by_css_selector('body')
        body.click()

        time.sleep(WAIT_INTERVAL)

        BROWSER.get_screenshot_as_file(SAVE_FILE_TEMP)

        BROWSER.close()

        im = Image.open(SAVE_FILE_TEMP)
        if not im.mode == 'RGB':
            im = im.convert('RGB')

        im.save(SAVE_FILE, "JPEG", quality=IMAGE_QUALITY)
        # im.save(SAVE_FILE, "PNG", quality=IMAGE_QUALITY)

        os.remove(SAVE_FILE_TEMP)

    except Exception as msg:
        message("error", str(msg))
        exit()

    message("ok", SAVE_FILE)

# -------------------------------------------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    init()
    check_url()
    create_display()
    create_browser()
    take_screenshot()
