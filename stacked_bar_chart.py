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
    # Determine data source and x-axis label
    if aggregation_level == 'Weekly':
        df = weekly_data
        x = 'Week'
    else:
        df = monthly_data
        x = 'Month'

    # Create stacked bar chart
    fig = px.bar(
        df,
        x=x,
        y='Energy Demand (kWh)',
        color='State',
        title=f'Energy Consumption by State ({aggregation_level} Aggregation)',
        labels={
            'Energy Demand (kWh)': 'Energy Demand (kWh)',
            x: aggregation_level.capitalize()
        },
        barmode='stack',
        color_discrete_sequence=['#4ecdc4', '#ff6b6b']  # Consistent color palette
    )

    # Apply consistent layout styling
    fig.update_layout(
        xaxis=dict(
            title=f"{aggregation_level.capitalize()}",
            tickangle=45,
            title_font=dict(size=14, color='#2c3e50'),
            tickfont=dict(size=12, color='#2c3e50')
        ),
        yaxis=dict(
            title="Energy Demand (kWh)",
            title_font=dict(size=14, color='#2c3e50'),
            tickfont=dict(size=12, color='#2c3e50')
        ),
        plot_bgcolor='rgba(240,240,240,0.95)',  # Light gray background for chart area
        title=dict(
            x=0.5,  # Center the title
            font=dict(size=16, color='#2c3e50')
        ),
        legend=dict(
            title=dict(text='Building State', font=dict(size=12, color='#2c3e50')),
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=30, b=40, l=20, r=20),  # Balanced margins
        hovermode='closest'  # Precise hover interaction
    )

    return fig
