import plotly.express as px

def occupancy_vs_energy_graph(data):
    return px.line(
        data,
        x='Time',
        y=['Occupancy Level (%)', 'Energy Demand (kWh)'],
        title='Occupancy and Energy Demand Over Time',
        labels={'value': 'Percentage/Energy', 'variable': 'Metric'}
    )
