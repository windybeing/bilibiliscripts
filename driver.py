from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
