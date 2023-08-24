import pandas as pd
import numpy as np

def read_ev_schedules(text_file_path):
    with open(text_file_path, 'r') as f:
        data = eval(f.read())  # Convert the text content into a dictionary using eval()

    vehicle_dataframes = {}  # Dictionary to store DataFrames for each vehicle

    for vehicle_num, items in data.items():
        rows = []
        for item in items:
            rows.append({**item, 'vehicle_num': vehicle_num})  # Add 'vehicle_num' to identify the vehicle

        df = pd.DataFrame(rows)
        vehicle_dataframes[vehicle_num] = df

    return vehicle_dataframes

def get_charging_profile(df,top_up_charge = False):
    
    if top_up_charge:
        df = top_up_charge(df)
    
    
    df = df[1:]
    df['soc_per_min'] = np.where(df['mode'] != 'charging', 0, df['soc_per_min'])
    
    # Create an empty dataframe with 1440 rows and a 'kWh_charged' column
    df_minute = pd.DataFrame({'kWh_charged': np.nan}, index=range(1440))

    # Iterate over each row in the original dataframe
    for _, row in df.iterrows():
        
        start_minute = int(row['time'])  # Starting minute of charging
        end_minute = start_minute + int(row['duration'])  # Ending minute of charging
    
        # Assign the 'soc_per_min' value to the corresponding minutes in the new dataframe
        df_minute.loc[start_minute:end_minute, 'kWh_charged'] = row['soc_per_min']

    # Fill any remaining NaN values with 0
    df_minute.fillna(0, inplace=True)
    

    return df_minute

def get_cumulative_charging_profile(vehicle_data):
    
    vehicle_charging_profiles = {}
    for key in vehicle_data:
        if 'soc_per_min' in vehicle_data[key].columns: # Filter out ICE vehicles
            vehicle_charging_profiles[key] = get_charging_profile(vehicle_data[key])
            

    # Get cumulative charging profile for all vehicles
    charging_profile = pd.DataFrame({'kWh_charged': np.zeros(1440)}, index=range(1440))
    for key in vehicle_charging_profiles:
        charging_profile['kWh_charged'] += vehicle_charging_profiles[key]['kWh_charged']
        
        
    return charging_profile 

def process_ev_schedule_data(filepath):
    all_vehicle_data  = read_ev_schedules(filepath)
    station_load_profile = get_cumulative_charging_profile(all_vehicle_data)
    
    return station_load_profile


def downsample_hourly_to_minutely(df):
    
    # Select every 60th row using array indexing
    hourly_charging_profile = df.rolling(window=60).sum().iloc[::60]

    # Reset the index to RangeIndex if desired
    hourly_charging_profile.reset_index(drop=True, inplace=True)

    hourly_charging_profile.plot()
    
    load_profile_hourly = hourly_charging_profile['kWh_charged'].values
    # fill NaN values with 0
    load_profile_hourly = np.nan_to_num(load_profile_hourly)
    
    return load_profile_hourly
