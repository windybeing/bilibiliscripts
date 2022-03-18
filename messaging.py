#-*- coding: utf-8
#!python3
import requests
import random
from datetime import datetime
from driver import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

biliCookieFileName = "biliCookie.txt"
biliRootUrl = "https://www.bilibili.com/"
biliLoginUrl = "https://passport.bilibili.com/login"

def getDevId():
    pattern = "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx"
    devId = ""
    for c in pattern:
        if c == 'x' or c == 'y':
            randomInt = random.randint(0, 15)
            if c == 'y':
                randomInt = 3 & randomInt | 8
            c = '{:x}'.format(randomInt).upper()
        devId += c
    print(devId)
    return devId

def getTS():
    dt = datetime.now()
    ts = datetime.timestamp(dt)
    ts = int(ts)
    print(ts)
    return ts

class Message:
    def __init__(self, cookieDict, receiverId, content, devId, ts) -> None:
        self.headers = { 'cookie': cookieDict.asString() }
        self.data = {
            'msg[sender_uid]': cookieDict.get('DedeUserID'),
            'msg[receiver_id]': receiverId,
            'msg[receiver_type]': '1',
            'msg[msg_type]': '1',
            'msg[content]': '{"content":"%s"}' % content,
            'msg[timestamp]': ts,
            'msg[dev_id]': devId,
            'csrf': cookieDict.get('bili_jct')
        }
    
    def send(self):
        response = requests.post('https://api.vc.bilibili.com/web_im/v1/web_im/send_msg', 
                                headers=self.headers, data=self.data)

if __name__=="__main__":
    try: 
        login(biliRootUrl, biliLoginUrl, biliCookieFileName)
        cookieDict = CookieDict(driver)
        devId = getDevId()
        ts = getTS()
        message = Message(cookieDict, '12076317', '可以了', devId, ts)
        message.send()
        # WebDriverWait(driver, 600).until(EC.number_of_windows_to_be(3))
    # except Exception as e:
    #     print("恭喜发现未知BUG，请联系皮皮！！")
    finally:
        driver.quit()