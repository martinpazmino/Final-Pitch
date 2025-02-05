from dash import Dash, dcc, html, Input, Output
from energy_calculation import calculate_energy_demand, energy_pie_chart
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from stacked_bar_chart import stacked_bar_chart
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
motor_energy_per_cycle = 6.5 # kWh per movement cycle
num_cycles = 90  # Total number of movements per year
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
    hole=0.4,  # Donut chart
    color_discrete_sequence=['#ff6b6b', '#4ecdc4']  # Custom colors for clarity
)

# Apply consistent styling
fig_pie_updated.update_layout(
    showlegend=True,  # Enable legend for better clarity
    legend=dict(
        orientation="h",  # Horizontal legend
        yanchor="bottom",
        y=-0.2,
        xanchor="center",
        x=0.5
    ),
    margin=dict(t=30, b=20, l=20, r=20),  # Balanced margins
    hovermode='closest',
    font=dict(color='#2c3e50', size=14),  # Consistent font style
    title_font=dict(size=16, color='#2c3e50')  # Title font styling
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
    html.H1("Energy Dashboard", style={'textAlign': 'center','marginBottom': '30px'}),

    # Adjusted Energy Demand Section
    html.Div([
        html.H1("Energy Demand vs Adjusted Energy Demand", style={'textAlign': 'center','marginBottom': '20px'}),

        # Line chart
        html.Div([
            html.H2("Energy Demand vs Adjusted Energy Demand", style={'textAlign': 'center', 'marginBottom': '20px'}),
            dcc.Graph(
                id='energy-demand-comparison',
                figure={
                    'data': [
                        go.Scatter(
                            x=data1['Date'],
                            y=data1['Energy Demand (kWh)'],
                            mode='lines+markers',
                            name='Energy Demand',
                            line=dict(color='#4ecdc4')
                        ),
                        go.Scatter(
                            x=data1['Date'],
                            y=data1['Adjusted Energy Demand (kWh)'],
                            mode='lines+markers',
                            name='Adjusted Energy Demand',
                            line=dict(color='#ff6b6b')  # Match theme color
                        )
                    ],
                    'layout': go.Layout(
                        xaxis={'title': "Date", 'automargin': True},
                        yaxis={'title': "Energy (kWh)", 'automargin': True},
                        legend={
                            'x': 0.01, 'y': 0.99, 'bgcolor': 'rgba(255,255,255,0.7)', 'bordercolor': '#ccc', 'borderwidth': 1
                        },
                        hovermode='x unified',
                        font=dict(color='#2c3e50', size=12),
                        margin=dict(t=50, b=40, l=60, r=40)
                    )
                },
                config={'displayModeBar': False}  # Hide toolbar
            )
        ], className="card", style={'padding': '20px ', 'backgroundColor': '#f9f9f9', 'borderRadius': '10px'})
    ]),
# Key Metrics Section
            html.Div([

                html.Div([
                    html.H3("Energy comparison", className="card-title"),
                    html.P(
                        f"Total energy demand: {total_energy_demand :.2f} kWh/ Total adjusted energy demand:{total_adjusted_energy_demand :.2f}kWh",
                        style={'fontSize': '20px'}),
                    dcc.Graph(
                        figure=px.bar(
                            y=[total_energy_demand, total_adjusted_energy_demand],
                            x=["Energy demand in kWh", " Adjusted Energy demand in kWh"],
                            color=["Without Concept", "With Concept"],
                            color_discrete_map={"Without Concept": "#4ecdc4", "With Concept": "#ff6b6b"}
                        ).update_layout(margin=dict(t=10), font=dict(color='#2c3e50')),
                        config={'displayModeBar': False}
                    )
                ], className="card"),
                html.Div([
            # Card 3: Solar Contribution
            html.Div([
                html.H3("Solar Contribution", className="card-title"),
                html.P(f"{solar_energy_covered:.2f} kWh (€{cost_solar_energy_covered:.2f})", style={'fontSize': '20px'}),
                dcc.Graph(
                    figure=px.pie(
                        values=[solar_energy_covered, total_combined_energy - solar_energy_covered],
                        names=["Solar", "Remaining"],
                        hole=0.4,
                        color_discrete_sequence=['#4ecdc4', '#ff6b6b']
                    ).update_layout(showlegend=False, margin=dict(t=10), font=dict(color='#2c3e50')),
                    config={'displayModeBar': False}
                )
            ], className="card"),



            # Card 4: Motor Energy Cost
            html.Div([
                html.H3("Motor Energy Cost year ", className="card-title"),
                html.P(f"{total_motor_energy} kWh/year x 0.20€ = €{motor_energy_cost:.2f}/year", style={'fontSize': '24px'}),
                dcc.Graph(
                    figure=px.bar(
                        x=["Motor Energy"],
                        y=[total_motor_energy],
                        title="",
                        color_discrete_sequence=['#ff6b6b ']
                    ).update_layout(margin=dict(t=10), font=dict(color='black')),
                    config={'displayModeBar': False}
                )
            ], className="card"),
        ], className="grid-row"),

        # Energy Demand Breakdown
        html.Div([
            html.H2("Energy Demand Breakdown", style={'textAlign': 'center', 'marginBottom': '20px'}),
            html.Div([
                dcc.Graph(
                    figure=px.pie(
                        values=[total_energy_demand, total_motor_energy ],
                        names=["Total Energy Demand", "Total Motor Energy"],
                        hole=0.4,
                        color_discrete_sequence=['#4ecdc4', '#ff6b6b']
                    ).update_layout(showlegend=False, margin=dict(t=10), font=dict(color='#2c3e50')),
                    config={'displayModeBar': False}
                )
            ], className="card", style={'padding': '15px'})
        ]),


        #waterfall
        html.Div([
            html.H2("Cost Savings Breakdown", style={
                'textAlign': 'center',
                'marginBottom': '20px',
                'color': '#2c3e50',
                'fontWeight': 'bold'
            }),
            html.Div([
                dcc.Graph(
                    figure=go.Figure(
                        go.Waterfall(
                            name="Cost Breakdown",
                            orientation="v",
                            measure=["absolute", "relative", "relative", "total"],
                            x=["Initial Cost", "Adaptation Savings", "Solar Savings", "Final Cost"],
                            textposition="outside",
                            text=[f"€{cost_total_energy_plus_motor:.2f}", f"-€{cost_difference_energy:.2f}",
                                  f"-€{cost_solar_energy_covered:.2f}", f"€{cost_with:.2f}"],
                            y=[cost_total_energy_plus_motor, -cost_difference_energy, -cost_solar_energy_covered,
                               cost_with],
                            connector={"line": {"color": "rgb(63, 63, 63)"}},
                            increasing={"marker": {"color": "#4ecdc4"}},  # Green for positive values
                            decreasing={"marker": {"color": "#ff6b6b"}},  # Red for negative values
                            totals={"marker": {"color": "#4ecdc4"}}  # Green for totals
                        )
                    ).update_layout(
                        title="Cost Savings Breakdown ",
                        title_font=dict(size=16, color='#2c3e50'),
                        yaxis=dict(
                            title="Cost (€)",
                            title_font=dict(size=14, color='#2c3e50'),
                            tickfont=dict(size=12, color='#2c3e50')
                        ),
                        xaxis=dict(
                            tickfont=dict(size=12, color='#2c3e50')
                        ),
                        plot_bgcolor='rgba(240,240,240,0.95)',  # Light gray background for chart
                        margin=dict(t=30, b=20, l=20, r=20),
                        hovermode='closest',
                        font=dict(color='#2c3e50'),
                        showlegend=False
                    ),
                    config={'displayModeBar': False}
                )
            ], className="card", style={
                'padding': '20px',
                'backgroundColor': '#ffffff',
                'boxShadow': '0 4px 8px rgba(0, 0, 0, 0.1)',
                'borderRadius': '10px'
            })
        ]),

# Card 2: Total Cost Comparison
            html.Div([
                html.H3("Cost Savings", className="card-title"),
                html.P(f"€{accurate_cost_savings:.2f}", style={'fontSize': '24px', 'color': 'green'}),
                dcc.Graph(
                    figure=px.bar(
                        x=["Without Concept", "With Concept"],
                        y=[cost_total_energy_demand, cost_with],
                        color=["Without Concept", "With Concept"],
                        color_discrete_map={"Without Concept": "#4ecdc4", "With Concept": "#ff6b6b"}
                    ).update_layout(margin=dict(t=10), font=dict(color='#2c3e50')),
                    config={'displayModeBar': False}
                )
            ], className="card"),
        ], className="grid-row"),

    ], style={'textAlign': 'center'})




if __name__ == "__main__":
    app.run_server(debug=True, port=8051)  # Use a different port (e.g., 8051)

