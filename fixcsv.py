import pandas as pd
# Reload the uploaded CSV file
file_path = r'C:\Users\HP\OneDrive\Documentos\martin\martin\Uni\3 semester\Schmidt\finalpitch\incident_radiation_21_06.csv'
data = pd.read_csv(file_path)

# Ensure proper formatting for the 'Time' column
data['Time'] = pd.to_datetime(data['Time'], errors='coerce')

# Get the starting time and total indices
start_time = data['Time'].min()
max_index = data['Point Index'].max()

# Calculate the time increment for 1.1 minutes per index
time_increment = pd.Timedelta(minutes=1.1)

# Generate a complete sequence of indices and times
full_index = pd.DataFrame({'Point Index': range(1, max_index + 1)})
full_index['Time'] = [start_time + i * time_increment for i in range(len(full_index))]

# Merge the full index with the original data
fixed_data = pd.merge(full_index, data, on=['Point Index', 'Time'], how='left')

# Interpolate missing 'Radiation (kWh/m²)' values
fixed_data['Radiation (kWh/m²)'] = fixed_data['Radiation (kWh/m²)'].interpolate(method='linear')

# Save the fixed dataset to a new CSV file
output_path = "incident_radiation_21_06_fixed.csv"  # Replace with desired output file path
fixed_data.to_csv(output_path, index=False)

print(f"Fixed file saved to: {output_path}")
