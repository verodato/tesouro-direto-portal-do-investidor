from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

'''
This module is responsible for managing chromedriver
'''

os.environ['WDM_LOG'] = '0'
os.environ['WDM_LOG_LEVEL'] = '0'


class Browser:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.headless = False
        serv_driver = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=serv_driver, options=options)

    def set_headers(self):
        raise NotImplementedError("Please implement this method")

    def close_driver(self):
        self.driver.close()
