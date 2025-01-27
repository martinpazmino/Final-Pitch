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
    # Data for pie chart
    energy_sources = ['Building Energy Demand', 'Motor Energy Demand']
    energy_values = [total_building_energy, total_motor_energy]

    # Create the pie chart
    fig = px.pie(
        values=energy_values,
        names=energy_sources,
        title='Annual Energy Demand Breakdown',
        hole=0.4  # Create a donut chart
    )
    return fig
