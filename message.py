#-*- coding: utf-8
#!python3
import requests
import random
from datetime import datetime
from driver import *
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

cookieFileName = "cookies/bilibili.txt"
rootUrl = "https://www.bilibili.com/"
loginUrl = "https://passport.bilibili.com/login"
msgUrl = "https://message.bilibili.com/#/reply"

receiverFileName = "私信名单.txt"
contentFileName = "私信内容.txt"

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
    return devId

def getTS():
    dt = datetime.now()
    ts = datetime.timestamp(dt)
    ts = int(ts)
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

def getReceiverList():
    res = []
    with open(receiverFileName, "r") as file:
        for line in file:
            res.append(line.split()[0])
    return res
        
def getContent():
    res = ""
    with open(contentFileName, "r") as file:
        res = file.read()
    res = res.replace('\n', '\\n')
    return res

def loginBilibili():
    while True:
        try:
            login(rootUrl, loginUrl, cookieFileName)
            driver.get(msgUrl)
            if not driver.current_url == msgUrl:
                os.remove(cookieFileName)
                raise LoginException
            break
        except LoginException:
            print("Cookie失效，需要重新登录一下")

if __name__=="__main__":
    try: 
        loginBilibili()
        cookieDict = CookieDict(driver)
        devId = getDevId()
        ts = getTS()
        content = getContent()
        receiverList = getReceiverList()

        for receiver in receiverList:
            message = Message(cookieDict, receiver, content, devId, ts)
            message.send()

    except Exception as e:
        print("恭喜发现未知BUG，请联系皮皮！！")
    finally:
        driver.quit()