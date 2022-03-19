#-*- coding: utf-8
#!python3
import os
import json
import requests
import re
from datetime import datetime
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchWindowException, TimeoutException
from selenium.webdriver.common.by import By
from driver import *

# 自动读取中奖页面的数量，默认每个页面20条可点开的记录
max_page_num = 2
# 被过滤掉的免费礼物
filterSet = {"么么哒", "学喵叫x3", "给你一拳！", "上船30元代金券"}

cookieFileName = "./cookies/kuabo.txt"
resultFileName = "获奖记录.txt"
rootUrl = "https://www.kuabo.cn"
loginUrl = "https://www.kuabo.cn/qq/login"
consoleUrl = "https://console.kuabo.cn/"
lotteryUrl = "https://console.kuabo.cn/lottery"
lotteryDetailsApi = "https://console.kuabo.cn/Lottery/detail?id=%s"

receiverFileName = "跨播私信名单.txt"

os.environ['WDM_LOG_LEVEL'] = '0'

def lottery():
    driver.get(lotteryUrl)
    if not driver.current_url == lotteryUrl:
        os.remove(cookieFileName)
        raise LoginException

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

def fetch():
    resultList = []
    i = 0
    page_num = 0
    cookieDict = CookieDict(driver)
    
    while True:
        # WebDriverWait(driver, 600).until(EC.number_of_windows_to_be(3))
        # WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        tbody = driver.find_element(by=By.TAG_NAME, value='tbody')
        rows = tbody.find_elements(by=By.TAG_NAME, value='tr')
        # WebDriverWait(driver, 600).until(EC.number_of_windows_to_be(2))

        for row in rows:
            linkTd = row.find_elements(by=By.TAG_NAME, value='td')[1]
            id = get_data_id(linkTd.get_attribute('innerHTML'))
            r = requests.post(lotteryDetailsApi%id, cookies = cookieDict.asDict(), verify=True)
            resultList = resultList + collect(r)
            i += 1
        page_num += 1
        if page_num >= max_page_num:
            break

        pagination = driver.find_element(By.CLASS_NAME, value='pagination').find_elements(By.TAG_NAME, value='li')
        next_button = pagination[len(pagination)-1]
        # WebDriverWait(driver, 5).until(EC.element_to_be_clickable(next_button)).click()
        driver.execute_script("arguments[0].click();", next_button)

        sleep(1)
    driver.minimize_window()
    return resultList

def process():
    while True:
        try:
            login(rootUrl, loginUrl, cookieFileName)
            lottery()
            break
        except LoginException:
            print("Cookie失效，需要重新登录一下")
    return fetch()

def remove_redundant_result(inputList):
    resultList = []
    inputList.reverse()
    maxDate = datetime.min
    for string in inputList:
        terms = string.split(" ")
        dateStr = terms[0] + " " + terms[1]
        date = datetime.strptime(dateStr, '[%Y/%m/%d %H:%M:%S]')
        if date >= maxDate:
            maxDate = date
            resultList.append(string)
    resultList.reverse()
    return resultList    

def filter_result(inputList):
    print("\033[1;32m<<<<<<<<<<< 请输入统计起始时间（格式类似[2022/2/28 22:59:53]，推荐复制上次获奖记录的最新日期） >>>>>>>>>>>\033[0m")
    text = input()
    if text == '':
        text = '[2022/2/28 22:59:53]'
    minDate = datetime.strptime(text, '[%Y/%m/%d %H:%M:%S]')

    resultList = []
    for string in inputList:
        terms = string.split(" ")
        dateStr = terms[0] + " " + terms[1]
        date = datetime.strptime(dateStr, '[%Y/%m/%d %H:%M:%S]')
        if date <= minDate:
            break

        item = terms[4]
        if item in filterSet:
            continue
        resultList.append(string)
    return resultList

def dump(inputList):
    with open(resultFileName, "w") as file:
        file.write('\n'.join(map(str, inputList)))

    id2Rewards = {}

    for string in inputList:
        terms = string.split(" ")
        nameId = terms[2]
        matches = re.findall("\(\d+\)", nameId)
        id = matches[-1][1:-1]
        
        rewards = id2Rewards.get(id)
        if rewards is None:
            rewards = [terms[4]]
            id2Rewards[id] = rewards
        else:
            rewards.append(terms[4])

    with open(receiverFileName, "w") as file:
        for id in id2Rewards.keys():
            rewards = id2Rewards[id]
            content = id + " " + ','.join(map(str, rewards)) + '\n'
            file.write(content)
    

if __name__=="__main__":
    # Time is money, my friend.
    # I sincerely hope that this script can save your time.
    #                                             ------皮皮
    try: 
        resultList = process()
        resultList = remove_redundant_result(resultList)
        resultList = filter_result(resultList)
        dump(resultList)
    except NoSuchWindowException:
        print("脚本运行时，自动打开的浏览器被你手动关闭了！不要这么做哦！")
    except TimeoutException:
        print("长时间未操作，所以这个脚本自己关闭了（")
    except ValueError:
        print("输入的时间格式不正确！")
    except Exception as e:
        print("恭喜发现未知BUG，请联系皮皮！！")
    finally:
        driver.quit()
        print("脚本执行完毕")