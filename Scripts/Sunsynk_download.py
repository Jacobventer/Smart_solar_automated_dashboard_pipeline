#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
import time
import json
import os
from datetime import datetime, timedelta


#Load credentials from json
with open('Config.json') as f:
    config = json.load(f)

USERNAME = config['sunsynk_username']
PASSWORD = config['sunsynk_password']
INVERTER_SN = config['sunsynk_inverter_sn']

driver_path = r"C:\WebDriver\chrome-win64\chromedriver-win64\chromedriver.exe"


#Set download folder
download_dir = r"D:\Users\jacov\Desktop\Persoonlike OneDrive\OneDrive\Persoonlik\Huis\Solar\Solar data\Solar data"

options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_dir,  # only for this Selenium session
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
}
options.add_experimental_option("prefs", prefs)


#Create driver
service = Service(executable_path=driver_path)
driver = webdriver.Chrome(service=service, options=options)

#Login to Sunsynk website
login_url = "https://www.sunsynk.net/login"
driver.get(login_url)

#Wait for the login form
username_field = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Please input your E-mail"]'))
)

#Enter Username and password - Login
username_field.send_keys(USERNAME)

password_field = driver.find_element(By.NAME, "txtPassword")
password_field.send_keys(PASSWORD)

login_button = driver.find_element(By.CSS_SELECTOR, "button.sunmit")
login_button.click()

print("Logged in")
time.sleep(5)

#Navigate to data page
data_url = "https://www.sunsynk.net/workdata/list"
driver.get(data_url)

WebDriverWait(driver, 15).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='选择日期']"))
)
print("Data page loaded")

#Determine date
today = datetime.now()
yesterday = today - timedelta(days=1)
yesterday_str = yesterday.strftime("%Y-%m-%d")

#Enter date into field
date_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder='选择日期']")
date_field.clear()
date_field.send_keys(yesterday_str)

#Enter Inverter SN
sn_field = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Please input SN']")
sn_field.clear()
sn_field.send_keys(INVERTER_SN)

#Click Search 
search_button = driver.find_element(By.CSS_SELECTOR, ".el-input-group__append button")
search_button.click()

print(f"Got data for {yesterday_str}")
time.sleep(5)

#Click Download button
download_button = WebDriverWait(driver, 15).until(
    EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Download')]]"))
)
download_button.click()

print("Download started into folder")

#Wait for file to finish 
time.sleep(15)

driver.quit()


# In[ ]:




