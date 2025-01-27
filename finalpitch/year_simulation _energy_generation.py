import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

# Define file paths
file_march = r"C:\Users\HP\OneDrive\Documentos\martin\martin\Uni\3 semester\Schmidt\finalpitch\incident_radiation_21_03.csv"
file_june = r"C:\Users\HP\OneDrive\Documentos\martin\martin\Uni\3 semester\Schmidt\finalpitch\incident_radiation_21_06.csv"
file_september = r"C:\Users\HP\OneDrive\Documentos\martin\martin\Uni\3 semester\Schmidt\finalpitch\incident_radiation_21_09.csv"
file_december = r"C:\Users\HP\OneDrive\Documentos\martin\martin\Uni\3 semester\Schmidt\finalpitch\incident_radiation_21_12.csv"
epw_file = r"C:\Users\HP\OneDrive\Documentos\martin\martin\Uni\3 semester\Schmidt\finalpitch\DEU_Augsburg.epw"
# Load the quarterly CSV data
data_march = pd.read_csv(file_march)
data_june = pd.read_csv(file_june)
data_september = pd.read_csv(file_september)
data_december = pd.read_csv(file_december)

# Load EPW data
epw_columns = [
    "Year", "Month", "Day", "Hour", "Minute", "Data Source and Uncertainty Flags",
    "Dry Bulb Temperature (°C)", "Dew Point Temperature (°C)", "Relative Humidity (%)",
    "Atmospheric Station Pressure (Pa)", "Extraterrestrial Horizontal Radiation (Wh/m²)",
    "Extraterrestrial Direct Normal Radiation (Wh/m²)", "Horizontal Infrared Radiation Intensity (Wh/m²)",
    "Global Horizontal Radiation (Wh/m²)", "Direct Normal Radiation (Wh/m²)",
    "Diffuse Horizontal Radiation (Wh/m²)", "Global Horizontal Illuminance (lux)",
    "Direct Normal Illuminance (lux)", "Diffuse Horizontal Illuminance (lux)",
    "Zenith Luminance (Cd/m²)", "Wind Direction (°)", "Wind Speed (m/s)",
    "Total Sky Cover (tenths)", "Opaque Sky Cover (tenths)",
    "Visibility (km)", "Ceiling Height (m)", "Present Weather Observation",
    "Present Weather Codes", "Precipitable Water (mm)", "Aerosol Optical Depth (dimensionless)",
    "Snow Depth (cm)", "Days Since Last Snowfall", "Albedo", "Liquid Precipitation Depth (mm)",
    "Liquid Precipitation Quantity (hr)"
]

# Load EPW file and extract relevant columns
epw_data = pd.read_csv(epw_file, skiprows=8, header=None, names=epw_columns)
epw_data["Date"] = pd.to_datetime(epw_data[["Year", "Month", "Day"]])

# Filter EPW data for relevant solar radiation information
epw_data = epw_data.groupby("Date")["Global Horizontal Radiation (Wh/m²)"].sum().reset_index()
epw_data.rename(columns={"Global Horizontal Radiation (Wh/m²)": "Radiation (Wh/m²)"}, inplace=True)

# Extract the time column and radiation values from each file
data_march['Date'] = pd.Timestamp("2025-03-21")
data_june['Date'] = pd.Timestamp("2025-06-21")
data_september['Date'] = pd.Timestamp("2025-09-21")
data_december['Date'] = pd.Timestamp("2025-12-21")

# Combine all data into a single DataFrame
all_data = pd.concat([
    data_march[['Date', 'Time', 'Radiation (kWh/m²)']],
    data_june[['Date', 'Time', 'Radiation (kWh/m²)']],
    data_september[['Date', 'Time', 'Radiation (kWh/m²)']],
    data_december[['Date', 'Time', 'Radiation (kWh/m²)']]
]).reset_index(drop=True)

# Generate a full year of dates (2025)
yearly_dates = pd.date_range(start="2025-01-01", end="2025-12-31", freq="D")

# Prepare an empty DataFrame for the yearly simulation
yearly_simulation = pd.DataFrame({'Date': yearly_dates})

# Interpolate radiation values for missing days using both quarterly data and EPW data
def interpolate_radiation(date_col, radiation_col):
    # Convert dates to ordinal for interpolation
    ordinal_dates = all_data['Date'].map(lambda x: x.toordinal())
    f_interp_quarterly = interp1d(ordinal_dates, all_data[radiation_col], kind='linear', fill_value="extrapolate")

    # Combine EPW data with quarterly data
    epw_ordinal_dates = epw_data['Date'].map(lambda x: x.toordinal())
    f_interp_epw = interp1d(epw_ordinal_dates, epw_data['Radiation (Wh/m²)'] / 1000, kind='linear', fill_value="extrapolate")

    # Interpolate radiation using both sources and average them
    interpolated_quarterly = f_interp_quarterly(yearly_simulation['Date'].map(lambda x: x.toordinal()))
    interpolated_epw = f_interp_epw(yearly_simulation['Date'].map(lambda x: x.toordinal()))

    return (interpolated_quarterly + interpolated_epw) / 2

yearly_simulation['Radiation (kWh/m²)'] = interpolate_radiation('Date', 'Radiation (kWh/m²)')

# Expand hourly data based on the interpolated daily radiation values
def expand_to_hourly(data, start_time, end_time):
    hourly_simulation = []
    total_hours = (pd.Timestamp(end_time) - pd.Timestamp(start_time)).seconds // 3600
    for _, row in data.iterrows():
        date = row['Date']
        daily_radiation = row['Radiation (kWh/m²)']
        hourly_radiation = daily_radiation / total_hours
        for hour in range(total_hours):
            time = pd.Timestamp(f"{date} {start_time}") + pd.Timedelta(hours=hour)
            hourly_simulation.append({
                'DateTime': time,
                'Radiation (kWh/m²)': hourly_radiation
            })
    return pd.DataFrame(hourly_simulation)

yearly_hourly_data = expand_to_hourly(yearly_simulation, start_time="06:00:00", end_time="20:00:00")

# Save the simulated data to a CSV file
yearly_hourly_data.to_csv("yearly_simulated_radiation.csv", index=False)

print("Yearly simulation completed and saved as 'yearly_simulated_radiation.csv'")
