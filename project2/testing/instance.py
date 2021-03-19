import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.opera import OperaDriverManager
import time
import datetime
import sys
if __name__ == '__main__':
    drivers = []
    for i in range(int(sys.argv[1])):
        drivers.append(webdriver.Chrome(ChromeDriverManager().install()))

        curDriver = drivers[-1]
        curDriver.get('http://localhost:5000/')
        curDriver.maximize_window()

        wait = WebDriverWait(curDriver, 10)

        username = "user" 
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="inputUsername"]'))).send_keys(username)
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="chatRoomName"]'))).send_keys('test')
        wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/div/form/button'))).click()

    print('Drivers completed.')