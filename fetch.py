#!python3
import os
import json
from tokenize import cookie_re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchWindowException, TimeoutException

cookieFileName = "cookie.txt"
cookie = None

lotteryUrl = "https://console.kuabo.cn/lottery"

def login(driver):
    if os.path.exists(cookieFileName):
        with open(cookieFileName, "r") as file:
            string = file.read()
            cookie = json.loads(string)
        driver.get("https://www.kuabo.cn")
        for c in cookie:
            driver.add_cookie(c)
    else:
        driver.get("https://www.kuabo.cn/login")
        WebDriverWait(driver, 60).until(EC.url_to_be("https://console.kuabo.cn/"))

        cookie = driver.get_cookies()
        with open(cookieFileName, "w") as file:
            file.write(json.dumps(cookie))

def lottery(driver):
    driver.get(lotteryUrl)
    if not driver.current_url == lotteryUrl:
        os.remove(cookieFileName)
        return False
    WebDriverWait(driver, 60).until(EC.number_of_windows_to_be(2))
    print("success!")

def fetch_data(driver):
    login(driver)
    success = lottery(driver)
    if not success:
        return False

if __name__=="__main__":
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try: 
        success = fetch_data(driver)
        if not success:
            fetch_data(driver)
    except NoSuchWindowException:
        print("脚本运行时，自动打开的浏览器被手动关闭了")
    except TimeoutException:
        print("长时间未响应，问题不大")
    except Exception as e:
        print("%s"%e)
        print("恭喜发现BUG，请联系皮皮！！")
    finally:
        driver.quit()
            
