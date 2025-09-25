#!/usr/bin/env python
# coding: utf-8

# In[5]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from datetime import datetime
import os
import matplotlib.pyplot as plt

# Path to ChromeDriver
driver_path = r"C:\WebDriver\chrome-win64\chromedriver-win64\chromedriver.exe"

def scrape_day1_all_hours():
    options = webdriver.ChromeOptions()
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        url = "https://en.tutiempo.net/solar-radiation/pretoria-irene.html"
        driver.get(url)

        # Wait until the first day's date is visible
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[3]/div[1]/div[1]/span"))
        )

        # Get Day 1 date (e.g., "August 26")
        day1_date = driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[3]/div[1]/div[1]/span").text.strip()

        # Add current year because site does not include it
        date_with_year = f"{day1_date} {datetime.now().year}"
        parsed_date = datetime.strptime(date_with_year, "%B %d %Y")
        formatted_date = parsed_date.strftime("%Y-%m-%d")  # e.g. 2025-08-21

        data = []

        # Loop through hour rows (07:00–17:00 → div[2] to div[12])
        for i in range(2, 13):
            try:
                hour = driver.find_element(By.XPATH, f"/html/body/div[2]/div[2]/div[3]/div[2]/div[{i}]/span[1]").text.strip()
                value = driver.find_element(By.XPATH, f"/html/body/div[2]/div[2]/div[3]/div[2]/div[{i}]/span[3]/strong").text.strip()
                data.append([formatted_date, hour, value])
            except Exception as e:
                print(f"Skipping row {i}: {e}")
                continue

        df = pd.DataFrame(data, columns=["Date", "Hour", "Radiation_Wm2"])
        df["Radiation_Wm2"] = pd.to_numeric(df["Radiation_Wm2"], errors="coerce")

        return df, formatted_date

    finally:
        driver.quit()


if __name__ == "__main__":
    df, formatted_date = scrape_day1_all_hours()
    print(df)

    # Calculate total daily radiation
    total_radiation = df["Radiation_Wm2"].sum()
    print(f"Total radiation for {formatted_date}: {total_radiation} Wh/m²")

    # Save CSV to fixed folder
    save_folder = r"D:\Users\jacov\Desktop\Persoonlike OneDrive\OneDrive\Persoonlik\Huis\Solar\Solar data\Solar Prediction"
    os.makedirs(save_folder, exist_ok=True)

    filename = f"{formatted_date} Solar prediction Irene.csv"
    save_path = os.path.join(save_folder, filename)
    df.to_csv(save_path, index=False)

    print(f"Saved {save_path}")




# In[ ]:




