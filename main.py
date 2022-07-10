from bs4 import BeautifulSoup

import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from selenium.common import exceptions

import time
import json
import re
import urllib.request
import requests

def writeDownloadLink(driver):
    # get all relevent logs from performance tab in Chrome Browser
    logs = driver.get_log("performance")
    with open("log.json", "w") as f:
        f.write("[")
        for log in logs:
            network_log = json.loads(log["message"])["message"]
            # look for Network.* (request, websocket, response)
            if ("Network.request" in network_log["method"]
            and "params" in network_log.keys()):
                try:
                    body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': network_log["params"]["requestId"]})
                    if (len(body["body"]) < 100 and body["body"].find("status_url") != -1):
                        f.write(json.dumps(body, indent=4))
                        f.write(", \n")
                except exceptions.WebDriverException:
                    # print('response.body is null')
                    continue
        f.write("]")
def readDownloadLink(driver):
    with open("log.json", "r") as f:
        text = f.read()
        newText = re.search("/en/task/.*-.*-.*-.*-.*", text).group(0)
        # print(text)
        # print(newText[:-6])
        video_server_link = "https://savett.cc" + newText[:-6]
        driver.get(video_server_link)
    video_download_link = re.search("https://.*.savett.cc/file/.*.mp4", driver.page_source).group(0)
    # print(video_download_link)
    return video_download_link

def downloadVideo(video_download_link):
    headers = {'User-Agent': 'Mozilla/5.0'}

    # get video from video_download_link
    response = requests.get(video_download_link, headers=headers)

    with open("test2.mp4", "wb") as f:
        # 1MB at a time
        for chunk in response.iter_content(chunk_size = 1024*1024): 
            if chunk: 
                f.write(chunk)

if __name__ == '__main__':
    tt_link = "https://www.tiktok.com/@tonysavv/video/7118286696093109550?_t=8TrtYVFLcPW&_r=1"

    # this code will be executed only once (main process)
    options = uc.ChromeOptions()
    # enable performance logging
    options.set_capability(
        "goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"}
    )
    options.add_argument("--headless")

    # start chrome driver
    driver = uc.Chrome(options=options)

    # get webpage
    driver.get("https://savett.cc") 

    # url input box
    input_box = driver.find_element(By.NAME, "url")

    # send video link
    input_box.send_keys(tt_link)
    input_box.send_keys(Keys.RETURN)

    time.sleep(5)

    # click download button
    download_button = driver.find_element(By.ID, "dl-btn")
    download_button.click()

    time.sleep(5)

    writeDownloadLink(driver)

    video_download_link = readDownloadLink(driver) 

    driver.close()

    downloadVideo(video_download_link) 
    
    print("DONE!")

