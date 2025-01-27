import pandas as pd
import plotly.express as px

def calculate_energy_demand(data, motor_energy_per_cycle, num_cycles):
    # Calculate total building energy demand
    total_building_energy = data['Energy Demand (kWh)'].sum()

    # Calculate total motor energy demand
    total_motor_energy = motor_energy_per_cycle * num_cycles

    # Total energy demand including motors
    total_combined_energy = total_building_energy + total_motor_energy

    return total_building_energy, total_motor_energy, total_combined_energy


def energy_pie_chart(total_building_energy, total_motor_energy):
    """
    Create a pie chart to display the breakdown of annual energy demand.

    Parameters:
        total_building_energy (float): The total energy demand of the building.
        total_motor_energy (float): The total energy demand from motor operations.

    Returns:
        fig (plotly.graph_objects.Figure): A styled donut chart for energy demand breakdown.
    """
    # Data for pie chart
    energy_sources = ['Building Energy Demand', 'Motor Energy Demand']
    energy_values = [total_building_energy, total_motor_energy]

    # Create the pie chart
    fig = px.pie(
        values=energy_values,
        names=energy_sources,
        title='Annual Energy Demand Breakdown',
        hole=0.4,  # Donut chart
        color_discrete_sequence=['#4ecdc4', '#ff6b6b']  # Custom colors for clarity
    )

    # Apply consistent styling
    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(t=30, b=20, l=20, r=20),
        hovermode='closest',
        font=dict(color='#2c3e50', size=14)
    )

    return fig