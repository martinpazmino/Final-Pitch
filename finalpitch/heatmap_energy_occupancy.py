import plotly.express as px
import pandas as pd

def heatmap_energy_occupancy(data, metric='Energy Demand (kWh)'):
    """
    Generate a heatmap to visualize patterns in energy demand and occupancy.

    Parameters:
        data (DataFrame): DataFrame with columns ['Time', 'Energy Demand (kWh)', 'Occupancy Level (%)'].
        metric (str): The metric to visualize, either 'Energy Demand (kWh)' or 'Occupancy Level (%)'.

    Returns:
        Figure: A Plotly heatmap figure.
    """
    # Ensure the 'Time' column is parsed as datetime
    data['Time'] = pd.to_datetime(data['Time'], errors='coerce')

    # Extract time of day and day of the week
    data['Hour'] = data['Time'].dt.hour
    data['Day Type'] = data['Time'].dt.dayofweek.apply(lambda x: 'Weekday' if x < 5 else 'Weekend')

    # Aggregate data to get mean energy demand and occupancy for each hour and day type
    heatmap_data = data.groupby(['Hour', 'Day Type']).agg({
        'Energy Demand (kWh)': 'mean',
        'Occupancy Level (%)': 'mean'
    }).reset_index()

    # Pivot the data for heatmap
    heatmap_pivot = heatmap_data.pivot(index='Day Type', columns='Hour', values=metric)

    # Create the heatmap
    fig = px.imshow(
        heatmap_pivot,
        color_continuous_scale="Viridis",
        title=f"Heatmap of {metric}",
        labels={"color": metric}
    )
    fig.update_layout(
        xaxis_title="Time of Day (Hour)",
        yaxis_title="Day Type",
        plot_bgcolor="rgba(240,240,240,0.95)",
        title_x=0.5
    )

    return fig
