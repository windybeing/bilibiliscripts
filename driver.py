import os
import json
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def login(rootUrl, loginURL, cookieFileName):
    if os.path.exists(cookieFileName):
        cookie = None
        with open(cookieFileName, "r") as file:
            string = file.read()
            cookie = json.loads(string)
        driver.get(rootUrl)
        for c in cookie:
            driver.add_cookie(c)
        driver.get(rootUrl)
    else:
        driver.get(loginURL)
        WebDriverWait(driver, 60).until(EC.url_to_be(rootUrl))

        cookie = driver.get_cookies()
        with open(cookieFileName, "w") as file:
            file.write(json.dumps(cookie))