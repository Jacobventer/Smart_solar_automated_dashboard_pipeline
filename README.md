#Smart Solar Optimize Data Pipeline

This project demonstrates an **end-to-end automated data pipeline** for solar energy monitoring.  
It was developed as part of a university assignment on **Data Quality and Data Wrangling**

---

## Project Overview

The pipeline automatically:
1. **Scrapes data** from three different web sources:
   - Solar radiation predictions
   - Local weather data
   - Inverter production/consumption logs
2. **Cleans and standardizes** the data into a unified tidy format
3. **Stores data in HDF5** using Pandas for efficient long-term use
4. **Generates dashboards** comparing:
   - Forecasted vs. actual PV production
   - Weather predictions
   - Daily consumption vs. generation
5. **Automates execution** with Windows Task Scheduler, so everything updates daily without manual intervention

---

## Example Dashboards

10 example static dashboards are available in the [`dashboards/`](Dashboards) folder.  
They can be viewed directly online thanks to GitHub Pages:

- [Dashboard – 2025-09-08](dashboards/solar_dashboard_2025-09-08.html)  
- [Dashboard – 2025-09-09](dashboards/solar_dashboard_2025-09-09.html)  
- [Dashboard – 2025-09-10](dashboards/solar_dashboard_2025-09-10.html)
  

Each dashboard includes:
- Predicted vs. actual solar PV production
- Weather conditions and codes
- Daily forecast vs. consumption comparison

---

## Code

All scripts are in the [`scripts/`](scripts) folder:

- `sWeather_scraper.py` → downloads weather forecasts  
- `Solar_prediction_daily.py` → downloads solar radiation predictions  
- `Sunsynk_download.py` → downloads inverter data 
- `Writing_scraped_files_to_HDF5.py` → combines all data into a single HDF5 time series file  
- `Solar_Smart_Dashboard_V4.py` → generates interactive Plotly Dash visualizations and saves daily static HTML dashboards  

---

## Automation

The full pipeline is scheduled to run **automatically once per day** using Windows Task Scheduler:

1. Scraper scripts run first and save CSV/XLSX data  
2. `writer_hdf5.py` consolidates into `smartsolar.h5`  
3. `dashboard.py` generates that day’s dashboard (`.html`) and saves it to the `dashboards/` folder  

This ensures a **fully automated "data-to-dashboard" workflow**.

---

## Tech Stack

- **Python** (pandas, numpy, plotly, dash)  
- **HDF5** (via pandas `HDFStore`)  
- **Automation** (Windows Task Scheduler)  
- **Visualization** (Plotly Dash + static HTML dashboards)  

---

## Learning Outcomes

This project demonstrates:
- Data scraping from heterogeneous sources
- Data cleaning, tidying, and unification
- Efficient storage formats (HDF5 for time series)
- Automated ETL pipelines
- Visualization and dashboarding with Plotly Dash
- Deployment of static dashboards for sharing (via GitHub Pages)

---

## 🔗 GitHub Pages

When GitHub Pages is enabled, dashboards will be available at:  
`(https://jacobventer.github.io/Smart_solar_automated_dashboard_pipeline/)`

---

