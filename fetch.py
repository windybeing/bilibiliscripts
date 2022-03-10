#-*- coding: utf-8
#!python3
import os
import json
import requests
from time import sleep
from tokenize import cookie_re
from unittest import result
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchWindowException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.common.by import By

# 自动读取中奖页面的数量，默认每个页面20条可点开的记录
max_page_num = 3

cookieFileName = "cookie.txt"
resultFileName = "输出.txt"
rootUrl = "https://www.kuabo.cn"
loginUrl = "https://www.kuabo.cn/qq/login"
consoleUrl = "https://console.kuabo.cn/"
lotteryUrl = "https://console.kuabo.cn/lottery"
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

requestCookies = dict()
filterSet = {"么么哒", "学喵叫x3", "给你一拳！"}
class LoginException(Exception):
    pass

def login():
    if os.path.exists(cookieFileName):
        cookie = None
        with open(cookieFileName, "r") as file:
            string = file.read()
            cookie = json.loads(string)
        driver.get(rootUrl)
        for c in cookie:
            driver.add_cookie(c)
    else:
        driver.get(loginUrl)
        WebDriverWait(driver, 60).until(EC.url_to_be(consoleUrl))

        cookie = driver.get_cookies()
        with open(cookieFileName, "w") as file:
            file.write(json.dumps(cookie))

def lottery():
    driver.get(lotteryUrl)
    if not driver.current_url == lotteryUrl:
        os.remove(cookieFileName)
        raise LoginException
    cookies = driver.get_cookies()
    for row in cookies:
        requestCookies[row['name']]=row['value']

def get_data_id(text):
    i = text.index('data-id="')
    j = text.index('" href')
    text = text[i+9:j]
    return text

def collect(content):
    string = content.text
    i = string.index('"data":"[')
    j = string.index('","closed_at"')
    string = string[i+11:j-3]
    string = string.replace("\\/", "/").encode('utf-8').decode('unicode_escape')
    res = string.split('","')
    return res

def fetch_one():
    result_list = []
    i = 0
    page_num = 0
    cookie = driver.get_cookies()
    
    while True:
        # WebDriverWait(driver, 600).until(EC.number_of_windows_to_be(3))
        # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        tbody = driver.find_element(by=By.TAG_NAME, value='tbody')
        rows = tbody.find_elements(by=By.TAG_NAME, value='tr')
        # WebDriverWait(driver, 600).until(EC.number_of_windows_to_be(2))

        for row in rows:
            linkTd = row.find_elements(by=By.TAG_NAME, value='td')[1]
            id = get_data_id(linkTd.get_attribute('innerHTML'))
            r = requests.post("https://console.kuabo.cn/Lottery/detail?id=%s"%id, cookies = requestCookies, verify=True)
            result_list = result_list + collect(r)
            i += 1
        page_num += 1
        if page_num >= max_page_num:
            break

        pagination = driver.find_element(By.CLASS_NAME, value='pagination').find_elements(By.TAG_NAME, value='li')
        next_button = pagination[len(pagination)-1]
        # WebDriverWait(driver, 5).until(EC.element_to_be_clickable(next_button)).click()
        driver.execute_script("arguments[0].click();", next_button)

        sleep(1)
    return result_list

def process():
    while True:
        try:
            login()
            lottery()
            break
        except LoginException:
            print("Cookie失效，需要重新登录一下")
    return fetch_one()

def filter_result(inputt_list):
    result_list = []
    for string in inputt_list:
        terms = string.split(" ")
        item = terms[4]
        if item in filterSet:
            continue
        result_list.append(string)
    return result_list

if __name__=="__main__":
    try: 
        result_list = process()
        result_list = filter_result(result_list)
        res_str = '\n'.join(map(str, result_list))
        with open(resultFileName, "w") as file:
            file.write(res_str)
    except NoSuchWindowException:
        print("脚本运行时，自动打开的浏览器被你手动关闭了！不要这么做哦！")
    except TimeoutException:
        print("长时间未操作，所以这个脚本自己关闭了（")
    # except Exception as e:
    #     print("%s"%e)
    #     print("恭喜发现BUG，请联系皮皮！！")
    finally:
        driver.quit()