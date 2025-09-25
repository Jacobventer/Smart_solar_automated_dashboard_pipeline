#!/usr/bin/env python
# coding: utf-8

# In[3]:


from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta, time
import plotly.io as pio

#Load Data from HDF5 file
HDF5_PATH = Path(r"D:\Users\jacov\Desktop\Persoonlike OneDrive\OneDrive\Persoonlik\Huis\Solar\Solar data\Solar HDF-5\smartsolar.h5")

def load_hdf_data(hdf5_path):
    with pd.HDFStore(hdf5_path, "r") as st:
        df = st["/timeseries/data"]
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date
    return df

df = load_hdf_data(HDF5_PATH)

#Weather Emoji Map 
WMO_EMOJIS = {
    0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️", 45: "🌫️", 48: "🌫️",
    51: "🌦️", 53: "🌦️", 55: "🌧️", 56: "🌧️❄️", 57: "🌧️❄️",
    61: "🌦️", 63: "🌧️", 65: "🌧️🌧️", 66: "🌧️❄️", 67: "🌧️❄️",
    71: "🌨️", 73: "🌨️", 75: "❄️", 77: "❄️",
    80: "🌦️", 81: "🌧️", 82: "⛈️", 85: "🌨️", 86: "❄️",
    95: "⛈️", 96: "⛈️❄️", 99: "⛈️❄️"
}

#Helper Functions
def plot_combined_solar(selected_date):
    """Combine yesterday's forecast vs actual and today's predicted PV"""
    today_df = df[df["date"] == selected_date].copy()
    yesterday = selected_date - timedelta(days=1)
    yesterday_df = df[df["date"] == yesterday].copy()
    
    factor = 0.0052  #This factor is used to calculate the total kwh from the w/m^2 of the Solar Prediction website. Each user will have its own factor

    #Yesterday forecast
    forecast_y = yesterday_df[yesterday_df["variable"]=="radiation_Wm2"].copy()
    forecast_y["predicted_kWh"] = forecast_y["value"] * factor
    forecast_y_hourly = forecast_y.set_index("timestamp")["predicted_kWh"]

    #Yesterday actual inverter 
    inverter_y = yesterday_df[yesterday_df["variable"].isin(["pv_west_W","pv_north_W"])].copy()
    inverter_wide = inverter_y.pivot_table(index="timestamp", columns="variable", values="value", aggfunc="mean")
    inverter_wide["pv_total_W"] = inverter_wide.fillna(0).sum(axis=1)
    inverter_5min = inverter_wide["pv_total_W"].resample("5min").mean() / 1000

    #Today predicted PV 
    forecast_t = today_df[today_df["variable"]=="radiation_Wm2"].copy()
    forecast_t["predicted_kWh"] = forecast_t["value"] * factor
    forecast_t_hourly = forecast_t.set_index("timestamp")["predicted_kWh"]

    #Build figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast_y_hourly.index, y=forecast_y_hourly.values, name="Yesterday Forecast", line=dict(color="red")))
    fig.add_trace(go.Scatter(x=inverter_5min.index, y=inverter_5min.values, name="Yesterday Actual", line=dict(color="blue")))
    fig.add_trace(go.Scatter(x=forecast_t_hourly.index, y=forecast_t_hourly.values, name="Today Predicted", line=dict(color="green", dash="dash")))

    fig.update_layout(
        template="plotly_white",
        title=f"Solar PV: Yesterday vs Today Predicted – {selected_date}",
        hovermode="x unified",
        yaxis_title="PV (kWh)"
    )

    #Totals annotation
    total_forecast_y = forecast_y_hourly.sum()
    total_actual_y = inverter_5min.sum() / 12  
    total_forecast_t = forecast_t_hourly.sum()

    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.55, y=1.1,
        text=f"<b>Yesterday Forecast:</b> {total_forecast_y:.1f} kWh<br>"
             f"<b>Yesterday Actual:</b> {total_actual_y:.1f} kWh<br>"
             f"<b>Today Predicted:</b> {total_forecast_t:.1f} kWh",
        showarrow=False,
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="rgba(0,0,0,0.9)",
        borderwidth=2,
        borderpad=6,
        font=dict(size=16, color="black")
    )

    return fig


def plot_daily_forecast_actual_consumption():
    factor = 0.0052
    
    #Predicted PV
    forecast = df[df["variable"]=="radiation_Wm2"].copy()
    forecast["predicted_kWh"] = forecast["value"]*factor
    pred_daily = forecast.groupby(forecast["timestamp"].dt.normalize())["predicted_kWh"].sum()
    
    #Actual PV
    actual = df[df["variable"]=="total_pv_production_KWH"].copy()
    actual_daily = actual.groupby(actual["timestamp"].dt.normalize())["value"].max()
    
    #Consumption
    cons = df[df["variable"]=="Consumption_KWH"].copy()
    cons_daily = cons.groupby(cons["timestamp"].dt.normalize())["value"].max()
    
    #Combine into a single DataFrame
    daily = pd.DataFrame({
        "Predicted": pred_daily,
        "Actual": actual_daily,
        "Consumption": cons_daily
    }).fillna(0).sort_index()  # Now all indices are Timestamps

    #Plot
    fig = go.Figure()
    for col, color in zip(daily.columns, ["red", "blue", "green"]):
        fig.add_trace(go.Bar(x=daily.index, y=daily[col], name=col, marker_color=color))
    
    fig.update_layout(
        template="plotly_white",
        barmode="group",
        title="Daily Forecast vs Actual PV vs Consumption",
        hovermode="x unified"
    )
    
    return fig

def plot_weather_graph(selected_date):
    day_df = df[df["date"] == selected_date]

    fig = go.Figure()

    temp = day_df[day_df["variable"]=="temperature_2m"]
    wind = day_df[day_df["variable"]=="wind_speed_10m"]
    cloud = day_df[day_df["variable"]=="cloud_cover"]

    fig.add_trace(go.Scatter(x=temp["timestamp"], y=temp["value"], name="Temp (°C)", line=dict(color="#E67E22")))
    fig.add_trace(go.Scatter(x=wind["timestamp"], y=wind["value"], name="Wind (m/s)", line=dict(color="purple")))
    fig.add_trace(go.Scatter(x=cloud["timestamp"], y=cloud["value"], name="Cloud (%)", line=dict(color="gray", dash="dot"), yaxis="y2"))

    rad = day_df[day_df["variable"]=="direct_radiation"]
    sun = day_df[day_df["variable"]=="sunshine_duration"]
    uv = day_df[day_df["variable"]=="uv_index"]
    codes = day_df[day_df["variable"]=="weather_code"].copy()
    codes["emoji"] = codes["value"].map(WMO_EMOJIS).fillna("❓")

    fig.add_trace(go.Scatter(x=rad["timestamp"], y=rad["value"], name="Radiation (W/m²)", line=dict(color="red")))
    fig.add_trace(go.Bar(x=sun["timestamp"], y=sun["value"], name="Sunshine (min)", marker_color="pink", opacity=0.5))
    fig.add_trace(go.Scatter(x=uv["timestamp"], y=uv["value"], name="UV Index", line=dict(color="gold"), yaxis="y3"))
    if not rad.empty:
        y_top = rad["value"].max() * 1.1
        fig.add_trace(go.Scatter(x=codes["timestamp"], y=[y_top]*len(codes), text=codes["emoji"], mode="text", name="Weather Emoji"))

    fig.update_layout(
        template="plotly_white", height=800, hovermode="x unified", 
        title=f"Predicted Weather – {selected_date}",
        yaxis=dict(title="Temp/Wind"),
        yaxis2=dict(title="Cloud (%)", overlaying="y", side="right"),
        yaxis3=dict(title="UV Index", overlaying="y", side="right")
    )
    return fig

#Dash App
app = Dash(__name__)
app.layout = html.Div([
    html.H1("Solar & Weather Dashboard", style={"text-align":"center"}),
    html.Div([
        html.Label("Select Date:"),
        dcc.DatePickerSingle(id="date-picker", date=datetime.now().date())
    ], style={"margin":"10px"}),
    dcc.Graph(id="weather-graph"),
    dcc.Graph(id="combined-solar"),
    dcc.Graph(id="daily-forecast-actual")
])


#Callbacks
@app.callback(
    Output("weather-graph", "figure"),
    Output("combined-solar", "figure"),
    Output("daily-forecast-actual", "figure"),
    Input("date-picker", "date")
)

def update_graphs(selected_date):
    if selected_date is None:
        selected_date = datetime.now().date()
    selected_date = pd.to_datetime(selected_date).date()

    #Combined solar: yesterday + today predicted
    combined_solar_fig = plot_combined_solar(selected_date)

    #Weather graphs
    weather_fig = plot_weather_graph(selected_date)

    #Daily forecast vs actual
    daily_fig = plot_daily_forecast_actual_consumption()
   
    
    return combined_solar_fig, weather_fig,  daily_fig

#Save static HTML file with current date
def save_static_html(selected_date):
    today_str = selected_date.strftime("%Y-%m-%d")

    # Fixed save location
    save_dir = r"C:\Users\jacov\anaconda_projects\Data Quality and Data Wrangling\Smart_Solar_Optimize_Dashboard\Dashboard"
    filename = f"{save_dir}\\solar_dashboard_{today_str}.html"

    weather_fig = plot_weather_graph(selected_date)
    combined_solar_fig = plot_combined_solar(selected_date)
    daily_fig = plot_daily_forecast_actual_consumption()

    # Convert figures to HTML snippets
    weather_html = pio.to_html(weather_fig, full_html=False, include_plotlyjs="cdn")
    combined_html = pio.to_html(combined_solar_fig, full_html=False, include_plotlyjs=False)
    daily_html = pio.to_html(daily_fig, full_html=False, include_plotlyjs=False)

    # Assemble static dashboard
    html_content = f"""
    <html>
    <head>
        <title>Solar Dashboard {today_str}</title>
    </head>
    <body>
        <h1>Solar & Weather Dashboard – {today_str}</h1>
        {weather_html}
        {combined_html}
        {daily_html}
    </body>
    </html>
    """

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Dashboard saved as {filename}")



#Run App
if __name__ == "__main__":
    # Get the date once, so all figs use the same day
    today = datetime.now().date()

    # Save static report
    save_static_html(today)
    
    app.run(mode="jupyterlab", debug=True, port=8065)


# In[ ]:




