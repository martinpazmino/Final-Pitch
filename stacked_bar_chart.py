import plotly.express as px

def stacked_bar_chart(aggregation_level, weekly_data, monthly_data):
    """
    Generate a stacked bar chart showing energy consumption by state for weekly or monthly aggregation.

    Parameters:
        aggregation_level (str): 'Weekly' or 'Monthly'.
        weekly_data (DataFrame): DataFrame with weekly aggregated data.
        monthly_data (DataFrame): DataFrame with monthly aggregated data.

    Returns:
        Figure: A Plotly figure object.
    """
    if aggregation_level == 'Weekly':
        df = weekly_data
        x = 'Week'
    else:
        df = monthly_data
        x = 'Month'

    fig = px.bar(
        df,
        x=x,
        y='Energy Demand (kWh)',
        color='State',
        title=f'Energy Consumption by State ({aggregation_level} Aggregation)',
        labels={'Energy Demand (kWh)': 'Energy Demand (kWh)', x: aggregation_level},
        barmode='stack'
    )
    fig.update_layout(
        xaxis=dict(tickangle=45),
        plot_bgcolor='rgba(240,240,240,0.95)',
        legend=dict(title='Building State'),
        title_x=0.5
    )
    return fig
