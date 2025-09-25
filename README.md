# Data Quality and Data Wrangling Project
## Smart Solar Opitimze automated dashboard pipeline
This project demonstrates an end-to-end automated data pipeline for a hypothetical solar mangement compony - Smart Solar Optimize.  
It was developed as part of a university assignment on Data Quality and Data Wrangling.


## Project Overview

The pipeline automatically:
1. Scrapes data from three different web sources:
   - Solar radiation predictions
   - Local weather data
   - Inverter production/consumption logs
2. Cleans and standardizes the data into a unified tidy format
3. Stores data in HDF5 using Pandas for efficient long-term use
4. Generates dashboard comparing:
   - Forecasted vs. actual PV production
   - Weather predictions
   - History of Daily consumption vs. generation PV vs. forecased PV
5. Automates execution with Windows Task Scheduler, so everything updates daily without manual intervention



## Example Dashboards

10 example static dashboards are available in the [`Dashboards/`](Dashboards) folder.  
Click on a dashboard then on "Download raw file" to open a dashboard

- [Dashboard – 2025-09-19](Dashboards/solar_dashboard_2025-09-19.html)  
- [Dashboard – 2025-09-18](Dashboards/solar_dashboard_2025-09-18.html)  
- [Dashboard – 2025-09-17](Dashboards/solar_dashboard_2025-09-17.html)

Each dashboard includes:
- Predicted vs. actual solar PV production with yesterdays and today's data
- Weather conditions and codes
- Daily forecast vs. consumption comparison bar graph

Example of a dashboard (19 Sept 2025):
Weather conditions and codes:
![image](https://github.com/Jacobventer/Smart_solar_automated_dashboard_pipeline/blob/main/Dashboard_screenshot/Weather%20dashboard.png)
Predicted vs. actual solar PV production with yesterdays and today's data:
![image](https://github.com/Jacobventer/Smart_solar_automated_dashboard_pipeline/blob/main/Dashboard_screenshot/Solar%20PV%20dashboard.png)
History fo Daily consumption vs. generation PV vs. forecased PV:
![image](https://github.com/Jacobventer/Smart_solar_automated_dashboard_pipeline/blob/main/Dashboard_screenshot/History%20dashboard.png)
  

## Code

All scripts are in the [`Scripts/`](Scripts) folder:

- `Weather_scraper.py` → downloads weather forecasts  
- `Solar_prediction_daily.py` → downloads solar radiation predictions  
- `Sunsynk_download.py` → downloads inverter data 
- `Writing_scraped_files_to_HDF5.py` → combines all data into a single HDF5 time series file  
- `Solar_Smart_Dashboard_V4.py` → generates interactive Plotly Dash visualizations and saves daily static HTML dashboards  



## Automation

The full pipeline is scheduled to run automatically once per day using Windows Task Scheduler:

1. 3 Scraper scripts run first and save CSV/XLSX data  
2. `Writing_scraped_files_to_HDF5.py` consolidates into `smartsolar.h5`  
3. `Solar_Smart_Dashboard_V4.py` generates that day’s dashboard (`.html`) and saves it to the `Dashboards/` folder  

This ensures a fully automated "data-to-dashboard" pipeline.

## Tech Stack

- **Python** (pandas, numpy, plotly, dash)  
- **HDF5** (via pandas `HDFStore`)  
- **Automation** (Windows Task Scheduler)  
- **Visualization** (Plotly Dash + static HTML dashboards)  


## Learning Outcomes

This project demonstrates:
- Data scraping from web sources
- Data cleaning, tidying, and unification
- Efficient storage formats (HDF5 for time series)
- Automated ETL pipelines
- Visualization and dashboarding with Plotly Dash
- Deployment of static dashboards for sharing (via GitHub Pages)


## GitHub Pages

When GitHub Pages is enabled, dashboards will be available at:  
`https://jacobventer.github.io/Smart_solar_automated_dashboard_pipeline/`



