import os
import json
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(service=Service(ChromeDriverManager(cache_valid_range=99999).install()))

def login(rootUrl, loginURL, cookieFileName):
    if os.path.exists(cookieFileName):
        cookie = None
        with open(cookieFileName, "r") as file:
            string = file.read()
            cookie = json.loads(string)
        driver.get(rootUrl)
        for c in cookie:
            driver.add_cookie(c)
    else:
        driver.get(loginURL)
        WebDriverWait(driver, 60).until(EC.url_to_be(rootUrl))

        cookie = driver.get_cookies()
        with open(cookieFileName, "w") as file:
            file.write(json.dumps(cookie))

class LoginException(Exception):
    pass
class DictNotFoundException(Exception):
    pass
class CancelException(Exception):
    pass

class CookieDict:
    def __init__(self, driver):
        self.cookieDict = dict()
        self.cookieString = ""
        cookies = driver.get_cookies()
        for row in cookies:
            name = row['name']
            value = row['value']
            self.cookieDict[name] = value
            self.cookieString += (name + "=" + value + "; ")
        self.cookieString = self.cookieString[0:-2]

    def get(self, key):
        value = self.cookieDict.get(key)
        if value is None:
            raise DictNotFoundException
        return value

    def asDict(self):
        return self.cookieDict

    def asString(self):
        return self.cookieString