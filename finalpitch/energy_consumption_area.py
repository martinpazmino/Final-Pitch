import plotly.express as px

def energy_consumption_by_area_chart(energy_by_area):
    """
    Generate a pie chart showing energy consumption by area.

    Parameters:
        energy_by_area (DataFrame): DataFrame with columns ['State', 'Energy Demand (kWh)'].

    Returns:
        Figure: A Plotly figure object.
    """
    return px.pie(
        energy_by_area,
        values='Energy Demand (kWh)',
        names='State',
        title='Energy Consumption: Expanded vs Contracted States'
    )
