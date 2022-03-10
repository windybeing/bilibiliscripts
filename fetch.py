#!python3
import os
import json
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
rootUrl = "https://www.kuabo.cn"
loginUrl = "https://www.kuabo.cn/qq/login"
consoleUrl = "https://console.kuabo.cn/"
lotteryUrl = "https://console.kuabo.cn/lottery"
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
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
        return False
    return True

def collect_content(content):
    res = content.split('<br>')
    return res

def fetch_one():
    result_list = []
    i = 0
    page_num = 0
    
    while True:
        # WebDriverWait(driver, 600).until(EC.number_of_windows_to_be(2))
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        tbody = driver.find_element(by=By.TAG_NAME, value='tbody')
        rows = tbody.find_elements(by=By.TAG_NAME, value='tr')

        for row in rows:
            linkTd = row.find_elements(by=By.TAG_NAME, value='td')[1]
            link = linkTd.find_element(by=By.TAG_NAME, value='a')
            driver.execute_script("arguments[0].click();", link)


            button = driver.find_element(by=By.XPATH, value="/html/body/div[1]/main/div[2]/div/div/div[1]/button")
            body = button.find_element(By.XPATH, value='../..').find_element(By.CLASS_NAME, value='modal-body')
            content = body.get_attribute('innerHTML')

            result_list = result_list + collect_content(content)
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(button)).click()
            # i += 1
            # print(i)
        page_num += 1
        if page_num >= max_page_num:
            break

        pagination = driver.find_element(By.CLASS_NAME, value='pagination').find_elements(By.TAG_NAME, value='li')
        next_button = pagination[len(pagination)-1]
        WebDriverWait(driver, 5).until(EC.element_to_be_clickable(next_button)).click()
        # WebDriverWait(driver, 600).until(EC.number_of_windows_to_be(2))
    return result_list

def process():
    while True:
        try:
            login()
            if not lottery():
                raise LoginException
            break
        except LoginException:
            print("Cookie失效，需要重新登录了")
    return fetch_one()

if __name__=="__main__":
    try: 
        result_list = process()
        # content = "[2022/3/10 22:40:04] 阿木不说话(119454154) 抽中 学喵叫x3<br>[2022/3/10 22:37:40] 100500111(9349401) 抽中 唇印明信片<br>[2022/3/10 22:37:40] 100500111(9349401) 抽中 唇印明信片"
        # res = collect_content(content)
        # result_list = result_list + res
        res_str = '\n'.join(map(str, result_list))
        print(res_str)
    except NoSuchWindowException:
        print("脚本运行时，自动打开的浏览器被你手动关闭了！不要这么做哦！")
    except TimeoutException:
        print("长时间未操作，所以这个脚本自己关闭了（")
    # except Exception as e:
    #     print("%s"%e)
    #     print("恭喜发现BUG，请联系皮皮！！")
    finally:
        driver.quit()
        print("Finish")
