# year_generation.py

import pandas as pd


def calculate_daily_radiation(data):
    """Calculate daily total radiation for a dataset."""
    data['Time'] = pd.to_datetime(data['Time'], errors='coerce')
    data.dropna(subset=['Time'], inplace=True)
    data['Date'] = data['Time'].dt.date
    return data.groupby('Date')['Radiation (kWh/m²)'].sum()/764


def estimate_monthly_radiation(daily_radiation, days_in_month):
    """Estimate monthly radiation from daily data."""
    average_daily_radiation = daily_radiation.mean()
    return average_daily_radiation * days_in_month


def estimate_annual_radiation(february_radiation, june_radiation, september_radiation, december_radiation):
    """Calculate annual radiation based on monthly estimates."""
    return (
            february_radiation * 2 +  # January & February
            june_radiation * 3 +  # May, June, & July
            september_radiation * 3 +  # August, September, & October
            december_radiation * 2  # November & December
    )


def calculate_radiation():
    """Load data, calculate daily radiation, and estimate annual generation."""
    # Load radiation data
    february_data = pd.read_csv(
        r'C:\Users\HP\OneDrive\Documentos\martin\martin\Uni\3 semester\Schmidt\finalpitch\incident_radiation_21_02_fixed.csv')
    june_data = pd.read_csv(
        r'C:\Users\HP\OneDrive\Documentos\martin\martin\Uni\3 semester\Schmidt\finalpitch\incident_radiation_21_06_fixed.csv')
    september_data = pd.read_csv(
        r'C:\Users\HP\OneDrive\Documentos\martin\martin\Uni\3 semester\Schmidt\finalpitch\incident_radiation_21_09_fixed.csv')
    december_data = pd.read_csv(
        r'C:\Users\HP\OneDrive\Documentos\martin\martin\Uni\3 semester\Schmidt\finalpitch\incident_radiation_21_12_fixed.csv')

    # Calculate daily radiation
    february_daily = calculate_daily_radiation(february_data)
    june_daily = calculate_daily_radiation(june_data)
    september_daily = calculate_daily_radiation(september_data)
    december_daily = calculate_daily_radiation(december_data)

    # Estimate monthly radiation
    february_radiation = estimate_monthly_radiation(february_daily, 28)
    june_radiation = estimate_monthly_radiation(june_daily, 30)
    september_radiation = estimate_monthly_radiation(september_daily, 30)
    december_radiation = estimate_monthly_radiation(december_daily, 31)

    # Estimate annual radiation
    annual_radiation = estimate_annual_radiation(february_radiation, june_radiation, september_radiation,
                                                 december_radiation)

    return annual_radiation
