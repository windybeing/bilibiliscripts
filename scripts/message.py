#-*- coding: utf-8
#!python3
import sys
import requests
import random
from datetime import datetime
from driver import *
from selenium.common.exceptions import NoSuchWindowException, TimeoutException

cookieFileName = "cookies/bilibili.txt"
rootUrl = "https://www.bilibili.com/"
loginUrl = "https://passport.bilibili.com/login"
msgUrl = "https://message.bilibili.com/#/reply"

receiverFileName = "私信名单.txt"
contentFileName = "私信内容.txt"
sailorsFileName = "舰长名单.txt"

os.environ['WDM_LOG_LEVEL'] = '0'

def get_dev_id():
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

def get_ts():
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
        requests.post('https://api.vc.bilibili.com/web_im/v1/web_im/send_msg', 
                                headers=self.headers, data=self.data)

def get_all_sailors(cookieDict):
    res = []
    myHeaders = { 'cookie': cookieDict.asString() }
    i = 1
    totalPages = 1
    while True:
        if i > totalPages:
            break
        myData = { 'page': i }        
        reply = requests.get('https://api.live.bilibili.com/xlive/web-ucenter/user/sailors',
                                headers=myHeaders, data=myData)
        pageJson = json.loads(reply.text)
        replyData = pageJson['data']
        totalPages = replyData['pageInfo']['totalPages']
        res += replyData['list']
        i += 1

    with open(sailorsFileName, "w") as file:
        file.write('\n'.join(map(str, res)))

def get_receiver_list():
    res = []
    with open(receiverFileName, "r") as file:
        for line in file:
            res.append(line.split()[0])
    print("\033[1;32m<<<<<<<<<<< 总计发送给%d名用户 >>>>>>>>>>>\033[0m"%len(res))
    return res
        
def get_content():
    res = ""
    with open(contentFileName, "r") as file:
        res = file.read()
    print("\033[1;32m<<<<<<<<<<< 准备发送的私信内容如下 >>>>>>>>>>>\033[0m")
    print(res)
    print("\033[1;32m<<<<<<<<<<< 输入yes确认发送 >>>>>>>>>>>\033[0m")
    text = input()
    if text != "yes":
        raise CancelException
    print("开始群发")
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
    driver.minimize_window()

if __name__=="__main__":
    func = 'message'
    if len(sys.argv) == 2:
        func = sys.argv[1]
    try: 
        loginBilibili()
        cookieDict = CookieDict(driver)
        if func == 'message':
            devId = get_dev_id()
            ts = get_ts()
            receiverList = get_receiver_list()
            content = get_content()

            for receiver in receiverList:
                message = Message(cookieDict, receiver, content, devId, ts)
                message.send()
        elif func == 'sailors':
            res = get_all_sailors(cookieDict)
        else:
            print('未指定具体功能')
    except NoSuchWindowException:
        print("脚本运行时，自动打开的浏览器被你手动关闭了！不要这么做哦！")
    except TimeoutException:
        print("长时间未操作，所以这个脚本自己关闭了（")
    except CancelException:
        print("主动取消群发")
    except Exception as e:
        print("恭喜发现未知BUG，请联系皮皮！！")
    finally:
        driver.quit()
        print("脚本执行完毕")
