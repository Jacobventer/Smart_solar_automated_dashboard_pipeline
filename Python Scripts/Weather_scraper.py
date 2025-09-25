#!/usr/bin/env python
# coding: utf-8

# In[3]:


#Weather data from "Open-Meteo"
#Yesterdays and next 3 day's data
import openmeteo_requests
import pandas as pd
import requests_cache
from datetime import datetime
import os
from retry_requests import retry

#Setup the Open-Meteo API client
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

#Select weather variables 

url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": -25.7449,
	"longitude": 28.1878,
	"hourly": ["temperature_2m", "precipitation_probability", "precipitation", "weather_code", "cloud_cover", "visibility", "wind_speed_10m",
               "soil_temperature_0cm", "uv_index", "uv_index_clear_sky", "sunshine_duration", "direct_radiation"],
	"timezone": "auto",
	"past_days": 1, #Yesterday
	"forecast_days": 3, #Next 3 days
}
responses = openmeteo.weather_api(url, params=params)

#Process location.
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

#Process hourly data. 
hourly = response.Hourly()
hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
hourly_precipitation_probability = hourly.Variables(1).ValuesAsNumpy()
hourly_precipitation = hourly.Variables(2).ValuesAsNumpy()
hourly_weather_code = hourly.Variables(3).ValuesAsNumpy()
hourly_cloud_cover = hourly.Variables(4).ValuesAsNumpy()
hourly_visibility = hourly.Variables(5).ValuesAsNumpy()
hourly_wind_speed_10m = hourly.Variables(6).ValuesAsNumpy()
hourly_soil_temperature_0cm = hourly.Variables(7).ValuesAsNumpy()
hourly_uv_index = hourly.Variables(8).ValuesAsNumpy()
hourly_uv_index_clear_sky = hourly.Variables(9).ValuesAsNumpy()
hourly_sunshine_duration = hourly.Variables(10).ValuesAsNumpy()
hourly_direct_radiation = hourly.Variables(11).ValuesAsNumpy()

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
)}

hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["precipitation_probability"] = hourly_precipitation_probability
hourly_data["precipitation"] = hourly_precipitation
hourly_data["weather_code"] = hourly_weather_code
hourly_data["cloud_cover"] = hourly_cloud_cover
hourly_data["visibility"] = hourly_visibility
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
hourly_data["soil_temperature_0cm"] = hourly_soil_temperature_0cm
hourly_data["uv_index"] = hourly_uv_index
hourly_data["uv_index_clear_sky"] = hourly_uv_index_clear_sky
hourly_data["sunshine_duration"] = hourly_sunshine_duration
hourly_data["direct_radiation"] = hourly_direct_radiation

hourly_dataframe = pd.DataFrame(data = hourly_data)

save_folder = r"D:\Users\jacov\Desktop\Persoonlike OneDrive\OneDrive\Persoonlik\Huis\Solar\Solar data\Weather"
os.makedirs(save_folder, exist_ok=True)

#Save file - Today's Date
todays_date = datetime.now().strftime("%Y-%m-%d")
filename = f"{todays_date} Weather Irene.csv"
save_path = os.path.join(save_folder, filename)

hourly_dataframe.to_csv(save_path, index=False)


print("\nHourly data\n", hourly_dataframe)
print()
print(f"Saved {filename}")


# In[ ]:




