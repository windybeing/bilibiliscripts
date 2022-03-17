#-*- coding: utf-8
#!python3
import os
import json
from driver import driver, login
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

biliCookieFileName = "biliCookie.txt"
biliRootUrl = "https://www.bilibili.com/"
biliLoginUrl = "https://passport.bilibili.com/login"



if __name__=="__main__":
    try: 
        login(biliRootUrl, biliLoginUrl, biliCookieFileName)
        
        WebDriverWait(driver, 600).until(EC.number_of_windows_to_be(3))
    # except Exception as e:
    #     print("恭喜发现未知BUG，请联系皮皮！！")
    finally:
        driver.quit()