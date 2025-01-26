import plotly.express as px

def monthly_summary_chart(monthly_summary):
    return px.bar(
        monthly_summary,
        x='Month',
        y=['Occupancy Level (%)', 'Energy Demand (kWh)'],
        barmode='group',
        title='Average Occupancy and Energy Demand by Month',
        labels={'value': 'Percentage/Energy', 'variable': 'Metric'}
    )
