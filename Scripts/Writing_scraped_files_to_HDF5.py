#!/usr/bin/env python
# coding: utf-8

# In[7]:


#Write data from 3 sources to one HDF5 file
import pandas as pd
from pathlib import Path
from datetime import date

#Config local path
base = Path(r"D:\Users\jacov\Desktop\Persoonlike OneDrive\OneDrive\Persoonlik\Huis\Solar\Solar data")
inverter_dir = base / "Solar data"
solar_dir    = base / "Solar Prediction"
weather_dir  = base / "Weather"
hdf5_path    = base / "Solar HDF-5" / "smartsolar.h5"

today = date.today().strftime("%Y-%m-%d")   #format: "2025-08-27"

#Helpers
def latest_file(folder: Path, exts=(".csv", ".xlsx")):
    files = [f for f in folder.iterdir() if f.suffix.lower() in exts]
    if not files:
        raise FileNotFoundError(f"No matching files in {folder}")
    today_files = [f for f in files if today in f.name]
    if today_files:
        return max(today_files, key=lambda f: f.stat().st_mtime)
    return max(files, key=lambda f: f.stat().st_mtime)

def all_files(folder: Path, exts=(".csv", ".xlsx")):
    files = [f for f in folder.iterdir() if f.suffix.lower() in exts]
    if not files:
        raise FileNotFoundError(f"No matching files in {folder}")
    return sorted(files, key=lambda f: f.stat().st_mtime)

def normalize_timestamp(df, col="timestamp"):
    df[col] = pd.to_datetime(df[col], errors="coerce")
    if df[col].dt.tz is not None:
        df[col] = df[col].dt.tz_convert("UTC").dt.tz_localize(None)
    return df

def tidy_weather(path: Path):
    df = pd.read_csv(path, parse_dates=["date"])
    df = df.rename(columns={"date": "timestamp"})
    long = df.melt(id_vars=["timestamp"], var_name="variable", value_name="value")
    long["source"] = "weather"
    long = long.dropna(subset=["timestamp"])  
    return long

def tidy_solar(path: Path):
    df = pd.read_csv(path)
    
    time_str = df['Date'].astype(str) + ' ' + df['Hour'].astype(str)
    df["timestamp"] = pd.to_datetime(time_str, errors='coerce')
    
    long = df.rename(columns={"Radiation_Wm2": "value"})[["timestamp", "value"]]
    long["variable"] = "radiation_Wm2"
    long["source"] = "solar_forecast"
    long = long.dropna(subset=["timestamp"])
    return long

def tidy_inverter(path: Path):
    if path.suffix.lower() == ".xlsx":
        df = pd.read_excel(path, header=2) 
    else:
        df = pd.read_csv(path, sep=",", low_memory=False)

    df.columns = df.columns.str.strip()

    if "Time" not in df.columns:
        raise ValueError(f"'Time' column not found in {path}, got: {df.columns[:10]}")

    df = df.rename(columns={"Time": "timestamp"})
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    keep = {
        "pvetoday(kWh)/108": "total_pv_production_KWH",
        "acTotalPower(W)/169": "ac_power_W",
        "loadTotalPower(W)/178": "total_load",
        "batteryEnergy(%)/184": "battery_SOC",
        "ppv1(W)/186": "pv_west_W",
        "ppv2(W)/187": "pv_north_W",
        "batteryPower(W)/190": "battery_power_W",
        "dailyUsed(kWh)/84": "Consumption_KWH",
        "gridBuyToday(kWh)/76": "grid_import_kWh"
    }

    cols = ["timestamp"] + [c for c in keep if c in df.columns]
    df = df[cols]

    long = df.melt(id_vars=["timestamp"], var_name="raw", value_name="value")
    long["variable"] = long["raw"].map(keep)
    long["source"] = "inverter"
    long = long.drop(columns="raw")
    long = long.dropna(subset=["timestamp"])
    return long

#Fixed an issue with loading files    
def load_all_solar(folder: Path):
    solar_files = all_files(folder, exts=(".csv",))
    solar_dfs   = [tidy_solar(f) for f in solar_files]
    return pd.concat(solar_dfs, ignore_index=True)

#Pipeline
def main():
    weather_file   = latest_file(weather_dir, (".csv",))
    inverter_file  = latest_file(inverter_dir, (".xlsx",))

    #Checks
    print("Using files:")
    print(" Weather:", weather_file.name)
    print(" Inverter:", inverter_file.name)
    print(" Solar: all CSVs in", solar_dir)

    weather  = tidy_weather(weather_file)
    solar    = load_all_solar(solar_dir)   
    inverter = tidy_inverter(inverter_file)

    #Normalize timestamps
    weather  = normalize_timestamp(weather)
    solar    = normalize_timestamp(solar)
    inverter = normalize_timestamp(inverter)

    new_data = pd.concat([weather, solar, inverter], ignore_index=True)

    with pd.HDFStore(hdf5_path, mode="a", complevel=9, complib="blosc:zstd") as st:
        if "/timeseries/data" in st:
            existing = st["/timeseries/data"]
        else:
            existing = pd.DataFrame(columns=["timestamp", "variable", "value", "source"])

        combined = pd.concat([existing, new_data], ignore_index=True)

        #Remove duplicates
        combined = combined.drop_duplicates(
            subset=["timestamp", "variable", "source"],
            keep="last"
        ).sort_values("timestamp")

        st.put(
            "/timeseries/data",
            combined,
            format="table",
            data_columns=["timestamp", "source", "variable"],
            append=False
        )
    
    print(f"Wrote {len(combined)} rows to {hdf5_path}")

if __name__ == "__main__":
    main()


# In[9]:


#Inspect
import pandas as pd

hdf5_path = r"D:\Users\jacov\Desktop\Persoonlike OneDrive\OneDrive\Persoonlik\Huis\Solar\Solar data\Solar HDF-5\smartsolar.h5"
df = pd.read_hdf(hdf5_path, "/timeseries/data")

print(df["timestamp"].min(), "→", df["timestamp"].max())
print(df["source"].value_counts())


# In[ ]:




