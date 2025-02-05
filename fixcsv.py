import plotly.express as px

# Data for the plot
area_data = {
    "State": ["Contracted Area (65 m²)", "Expanded Area (135 m²)"],
    "Area (m²)": [65, 135]
}

# Create a donut chart
fig = px.pie(
    area_data,
    values="Area (m²)",
    names="State",
    title="Contracted vs Expanded Building Area",
    hole=0.5,  # Creates a donut chart
    color_discrete_sequence=["#4ecdc4", "#ff6b6b"]  # Custom colors
)

# Update layout for styling
fig.update_layout(
    title_font=dict(size=16, color='#2c3e50'),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="center",
        x=0.5
    ),
    margin=dict(t=30, b=20, l=20, r=20),
    font=dict(color='#2c3e50')
)

# Show the chart
fig.show()
