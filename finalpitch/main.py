from dash import Dash, dcc, html, Input, Output
from occupancy_vs_energy import occupancy_vs_energy_graph
from solar_energy import solar_energy_chart
from energy_consumption_area import energy_consumption_by_area_chart
from stacked_bar_chart import stacked_bar_chart
from heatmap_energy_occupancy import heatmap_energy_occupancy
from energy_calculation import calculate_energy_demand, energy_pie_chart
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from year_generation import calculate_radiation

# Load the adjusted data
adjusted_data_path = "Adjusted_Daily_Energy_Demand.csv"
data1 = pd.read_csv(adjusted_data_path)

# Ensure the 'Date' column is present
if 'Date' not in data1.columns:
    if 'Time' in data1.columns:
        data1['Time'] = pd.to_datetime(data1['Time'])
        data1['Date'] = data1['Time'].dt.date  # Extract date from Time column
    else:
        raise KeyError("Neither 'Date' nor 'Time' column is available in the dataset.")

# Load the main data
data = pd.read_csv("occupancy_energy_demand.csv")
data['Time'] = pd.to_datetime(data['Time'], errors='coerce')
data.dropna(subset=['Time'], inplace=True)  # Drop rows with invalid time
data['Date'] = data['Time'].dt.date  # Extract the date
data['Week'] = data['Time'].dt.isocalendar().week  # Extract week number
data['Month'] = data['Time'].dt.month  # Extract month
data['State'] = data['Occupancy Level (%)'].apply(lambda x: 'Expanded (135 m²)' if x > 50 else 'Contracted (65 m²)')

# Constants
motor_energy_per_cycle = 160  # kWh per movement cycle
num_cycles = 40  # Total number of movements per year
pannel_area= 64



# Calculate total energy demand and total adjusted energy demand
total_energy_demand = data1['Energy Demand (kWh)'].sum()
total_adjusted_energy_demand = data1['Adjusted Energy Demand (kWh)'].sum()
difference_energy = total_energy_demand - total_adjusted_energy_demand

# Define the cost per kWh
cost_per_kwh = 0.20  # Adjust based on actual costs
cost_savings = difference_energy * cost_per_kwh
# Perform calculations
total_building_energy, total_motor_energy, total_combined_energy = calculate_energy_demand(
    data=data,
    motor_energy_per_cycle=motor_energy_per_cycle,
    num_cycles=num_cycles
)

# Create pie chart
pie_chart_figure = energy_pie_chart(total_building_energy, total_motor_energy)


# Solar panel efficiency
reduction_tilt_angle= 0.6
solar_panel_efficiency = 0.20
annual_radiation = calculate_radiation()
annual_energy_generation =pannel_area*annual_radiation * solar_panel_efficiency
solar_energy_covered=pannel_area*annual_radiation*solar_panel_efficiency*reduction_tilt_angle

fig_pie_updated = px.pie(
    values=[total_combined_energy - solar_energy_covered, solar_energy_covered],
    names=["Remaining Energy Demand", "Solar Energy Contribution"],
    title="Updated Energy Contribution: Solar vs. Remaining Demand",
    hole=0.4
)

# Aggregate data for charts
weekly_data = data.groupby(['Week', 'State']).agg({'Energy Demand (kWh)': 'sum'}).reset_index()
monthly_data = data.groupby(['Month', 'State']).agg({'Energy Demand (kWh)': 'sum'}).reset_index()
monthly_summary = data.groupby('Month').agg({
    'Occupancy Level (%)': 'mean',
    'Energy Demand (kWh)': 'mean'
}).reset_index()

# Load the combined solar energy data
combined_data = pd.concat([
    pd.read_csv("incident_radiation_21_02_fixed.csv").assign(Month="March"),
    pd.read_csv("incident_radiation_21_06_fixed.csv").assign(Month="June"),
    pd.read_csv("incident_radiation_21_09_fixed.csv").assign(Month="September"),
    pd.read_csv("incident_radiation_21_12_fixed.csv").assign(Month="December")
])
combined_data['DateTime'] = pd.to_datetime(combined_data['Time'], errors='coerce')  # Ensure proper time parsing
combined_data.dropna(subset=['DateTime'], inplace=True)  # Drop rows with invalid DateTime
combined_data['Hour'] = combined_data['DateTime'].dt.hour  # Extract hour for the x-axis

#Cost Total energy demand
cost_total_energy_demand= total_energy_demand* cost_per_kwh
# Total energy demand including motor energy
total_energy_plus_motor = total_energy_demand + total_motor_energy
#Cost total_energy_plus_motor
cost_total_energy_plus_motor= total_energy_plus_motor* cost_per_kwh
# Calculate motor energy cost
motor_energy_cost = total_motor_energy * cost_per_kwh

#cost solar energy covered
cost_solar_energy_covered= solar_energy_covered*cost_per_kwh


#difference_energy per cost

cost_difference_energy= difference_energy* cost_per_kwh

#cost with proposal

cost_with= cost_total_energy_plus_motor-cost_difference_energy-cost_solar_energy_covered

# Accurate cost savings
accurate_cost_savings = cost_difference_energy+cost_solar_energy_covered


# Dash app initialization
app = Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Energy Dashboard", style={'textAlign': 'center'}),

    # Occupancy vs Energy Demand
    html.Div([
        html.H2("Occupancy vs Energy Demand"),
        dcc.Graph(figure=occupancy_vs_energy_graph(data))
    ]),

    # Solar Energy Contribution (Linear Chart for All Months)
    html.Div([
        html.H2("Solar Energy Contribution Across All Months"),
        dcc.Graph(id='solar-energy-linear-chart')
    ]),


    # Energy Consumption by Area
    html.Div([
        html.H2("Energy Consumption by Area"),
        dcc.Graph(figure=energy_consumption_by_area_chart(data.groupby('State')['Energy Demand (kWh)'].sum().reset_index()))
    ]),

    # Energy demand
    html.Div([
        html.H2("Energy Demand Breakdown"),
        dcc.Graph(figure=pie_chart_figure)
    ]),

    #year_generation
    html.Div([
        html.H2("Updated Energy Contribution: Solar vs. Remaining Demand"),
        dcc.Graph(figure=fig_pie_updated)
    ]),


    # Stacked Bar Chart
    html.Div([
        html.H2("Energy Consumption by State"),
        dcc.RadioItems(
            id='aggregation-level',
            options=[
                {'label': 'Weekly', 'value': 'Weekly'},
                {'label': 'Monthly', 'value': 'Monthly'}
            ],
            value='Weekly',
            inline=True
        ),
        dcc.Graph(id='stacked-bar-chart')
    ]),

    # Heatmap
    html.Div([
        html.H2("Heatmap of Energy Demand and Occupancy"),
        dcc.RadioItems(
            id='metric-selector',
            options=[
                {'label': 'Energy Demand (kWh)', 'value': 'Energy Demand (kWh)'},
                {'label': 'Occupancy Level (%)', 'value': 'Occupancy Level (%)'}
            ],
            value='Energy Demand (kWh)',  # Default selection
            inline=True
        ),
        dcc.Graph(id='heatmap-chart')
    ]),
    #adjusted energy demand
    html.Div([
        html.H1("Energy Demand vs Adjusted Energy Demand", style={'textAlign': 'center'}),

        # Line chart
        dcc.Graph(
            id='energy-demand-comparison',
            figure={
                'data': [
                    go.Scatter(
                        x=data1['Date'],
                        y=data1['Energy Demand (kWh)'],
                        mode='lines+markers',
                        name='Energy Demand'
                    ),
                    go.Scatter(
                        x=data1['Date'],
                        y=data1['Adjusted Energy Demand (kWh)'],
                        mode='lines+markers',
                        name='Adjusted Energy Demand'
                    )
                ],
                'layout': go.Layout(
                    title="Energy Demand vs Adjusted Energy Demand",
                    xaxis={'title': "Date"},
                    yaxis={'title': "Energy (kWh)"},
                    legend={'x': 0, 'y': 1},
                    hovermode='closest'
                )
            }
        ),

        # Difference annotation
        html.Div([
            html.H2(f"Total Energy Demand: {total_energy_demand:.2f} kWh"),
            html.H2(f"Cost of Total Energy Demand: ${cost_total_energy_demand:.2f}"),
            html.H2(f"Total Energy + Motor Energy Demand: {total_energy_plus_motor:.2f} kWh"),
            html.H2(f"Cost of Total Energy Demand + Motor Energy Demand: ${cost_total_energy_plus_motor:.2f}"),
            html.H2(f"Motor Energy Cost: ${motor_energy_cost:.2f}"),
            html.H2(f"Solar Contribution: {solar_energy_covered:.2f} kWh"),
            html.H2(f"Cost Solar Contribution: ${cost_solar_energy_covered:.2f}"),
            html.H2(f"Difference of energy by adaption: {difference_energy:.2f} kWh"),
            html.H2(f"Cost of difference of energy by adaption: ${cost_difference_energy:.2f} "),
            html.H2(f"Cost Without Concept: ${cost_total_energy_demand:.2f}"),
            html.H2(f"Cost With Concept: ${cost_with:.2f}"),
            html.H2(f" Approximate Cost Savings: ${accurate_cost_savings:.2f}"),
        ], style={'textAlign': 'center'}),

    ])

])

# Callbacks
@app.callback(
    Output('solar-energy-linear-chart', 'figure'),
    Input('solar-energy-linear-chart', 'id')  # Dummy input to trigger rendering
)
def display_solar_energy_linear_chart(_):
    # Ensure data for all months is included
    return solar_energy_chart(combined_data)


@app.callback(
    Output('stacked-bar-chart', 'figure'),
    Input('aggregation-level', 'value')
)
def update_stacked_bar(aggregation_level):
    return stacked_bar_chart(aggregation_level, weekly_data, monthly_data)

@app.callback(
    Output('heatmap-chart', 'figure'),
    Input('metric-selector', 'value')
)
def update_heatmap(selected_metric):
    return heatmap_energy_occupancy(data, metric=selected_metric)

# Run the Dash app
if __name__ == "__main__":
    app.run_server(debug=True)
