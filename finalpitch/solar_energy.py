import plotly.express as px

def solar_energy_chart(data):
    """
    Generate a linear chart to visualize solar energy contribution across all months.

    Parameters:
        data (DataFrame): Combined DataFrame with solar energy data for all months.

    Returns:
        Figure: A Plotly linear chart figure.
    """
    fig = px.line(
        data,
        x='Hour',
        y='Radiation (kWh/m²)',
        color='Month',  # Differentiate months by color
        title='Solar Energy Contribution Across All Months',
        labels={
            'Hour': 'Time of Day (Hour)',
            'Radiation (kWh/m²)': 'Solar Energy Generated (kWh/m²)',
            'Month': 'Month'
        }
    )
    fig.update_layout(
        xaxis_title='Time of Day (Hour)',
        yaxis_title='Solar Energy Contribution (kWh/m²)',
        plot_bgcolor='rgba(240,240,240,0.95)',
        title_x=0.5
    )
    return fig

