import numpy as np
import matplotlib.pyplot as plt
import datetime
import pysolar.solar as solar

########### Get parameters ########### 

def get_user_input():
    params = {}

    # Ask for input and store in the dictionary
    params['name'] = input("Enter your name: ")


    return params 

########### Charging load ########### 

def simulate_charging_load_profile(total_days, total_time,
                             time_resolution,
                             num_vehicles,
                             charging_power):
    '''
    This function simulates a charging load profile for a fleet of EVs at a charging station, given the number of EVs, the charging power, the total simulation time, and the desired time resolution
    
    '''
    
    # Generate random charging start times and durations for each EV
    np.random.seed(42)  # Set a seed for reproducibility
    start_times = np.random.uniform(low=0, high=total_time, size=(num_vehicles, total_days))
    durations = np.random.uniform(low=1, high=4, size=(num_vehicles, total_days))

    # Create the time axis
    time = np.arange(0, total_time, time_resolution)

    # Initialize the load profile
    load_profile = np.zeros_like(time)

    # Calculate the EV load profile for each day
    for day in range(total_days):
        for i in range(num_vehicles):
            start_time = start_times[i, day]
            duration = durations[i, day]
            end_time = start_time + duration

            # Calculate the charging load during the charging period
            mask = (time >= start_time) & (time < end_time)
            load_profile[mask] += charging_power

    # Plot the EV load profile
    plt.plot(time, load_profile)
    plt.xlabel('Time (hours)')
    plt.ylabel('Power (kW)')
    plt.title('Electric Vehicle Load Profile')
    plt.grid(True)
    plt.show()
    
    return load_profile 

########### Insolation ########### 

def simulate_insolation_profile(latitude, longitude, time_resolution, timezone):
    '''
    This function simulates a solar insolation profile for a given location and time period, as well as the average daily insolation profile for the same location. The function returns the simulated insolation profile and the average daily insolation profile'''

    # Get the current year
    current_year = datetime.datetime.now().year

    # Create a datetime object for the start of the year
    start_time = timezone.localize(datetime.datetime(current_year, 1, 1))

    # Create a datetime object for the start of the next year
    end_time = start_time + datetime.timedelta(days=365)

    # Initialize an array to store the accumulated insolation for each time step
    insolation_accumulated = np.zeros(int(24 * 60 / time_resolution))

    # Initialize a counter for the number of days
    num_days = 0

    # Initialize a list to hold values for all of the hours
    annual_insolation_profile = []

    # Iterate over each day of the year
    time = start_time
    while time < end_time:
        # Calculate the insolation for each time step of the day
        for t in range(int(24 * 60 / time_resolution)):
            time_step = time + datetime.timedelta(minutes=t * time_resolution)
            altitude_deg = solar.get_altitude(latitude, longitude, time_step)
            insolation = solar.radiation.get_radiation_direct(time_step, altitude_deg)
            
            # Check for NaN values and accumulate the insolation
            if not np.isnan(insolation):
                insolation_accumulated[t] += insolation
                annual_insolation_profile.append(insolation)
            else:
                annual_insolation_profile.append(0)
        
        # Increment the day counter
        num_days += 1
        
        # Move to the next day
        time += datetime.timedelta(days=1)

    # Calculate the average insolation for each time step
    daily_insolation_profile = insolation_accumulated / num_days
    
    
    # Calculate the average insolation for each time step
    insolation_profile = insolation_accumulated / num_days

    # Plot the average daily insolation profile
    plt.plot(insolation_profile)
    plt.xlabel('Time of Day (minutes)')
    plt.ylabel('Insolation (W/m^2)')
    plt.title('Average Daily Insolation Profile')
    plt.grid(True)
    plt.show()


    # Plot the annual insolation profile
    plt.plot(annual_insolation_profile)
    plt.xlabel('Time of Day (minutes)')
    plt.ylabel('Insolation (W/m^2)')
    plt.title('Annual Insolation Profile')
    plt.grid(True)
    plt.show()
    
    
    return daily_insolation_profile, annual_insolation_profile 

########### PV Output ########### 

def get_pv_output(insolation_profile, pv_efficiency, pv_capacity):
    '''
    This function obtains the solar PV output profile given a solar insolation profile, PV efficiency, and PV capacity. The function returns the PV output profile.'''

    # Calculate daily PV output profile
    pv_output_profile = [pv_capacity * pv_efficiency * i / 1000 for i in insolation_profile]

    # # Plot the average daily PV output profile 
    # plt.plot(pv_output_profile)
    # plt.xlabel('Time of Day (minutes)')
    # plt.ylabel('PV Output (kW)')
    # plt.grid(True)
    # plt.show()
    
    return pv_output_profile


def simulate_battery_storage(load_profile, pv_output_profile, max_battery_capacity):
    battery_state = 0  # Initial state of the battery

    storage_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy stored in the battery
    discharge_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy discharged from the battery
    curtailed_energies = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the wasted energies
    battery_states = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the battery state

    for hour, load in enumerate(load_profile):
        net_load = load - pv_output_profile[hour]  # Calculate the net load profile
        
        battery_room = max_battery_capacity - battery_state # Calculate the amount of room left in the battery
        
        energy_stored = 0
        energy_discharged = 0
        curtailed_energy = 0
        
        if net_load < 0:
            # The PV system is producing more energy than the load requires
            # Charge the battery with the excess energy
            energy_stored = min(battery_room, -net_load)
            battery_state = battery_state + energy_stored
            curtailed_energy = -net_load - energy_stored
            
        elif net_load > 0:
            # The PV system is producing less energy than the load requires
            # Discharge the battery to assist with the load 
            energy_discharged = min(battery_state, net_load)
            battery_state = battery_state - energy_discharged
            
        curtailed_energies[hour] = curtailed_energy
        battery_states[hour] = battery_state
        storage_profile[hour] = energy_stored
        discharge_profile[hour] = energy_discharged
        
    pv_with_battery_output_profile = pv_output_profile + discharge_profile - storage_profile 
  #  load_profile_with_battery = load_profile - pv_with_battery_output_profile
    
    return pv_with_battery_output_profile

########### Loadshedding ########### 

def generate_loadshedding_schedule(loadshedding_probability, set_random_seed = True):
    schedule = []
    hours_in_year = 365 * 24  # Assuming a non-leap year
    
    #set random seed
    if set_random_seed:
        random.seed(0)
    
    for _ in range(hours_in_year):
        # Generate a random value between 0 and 1
        random_value = random.random()
        
        # Determine if load shedding occurs based on the random value
        # Adjust the threshold value to control the frequency of load shedding
        if random_value < loadshedding_probability:
            schedule.append(True)  # Load shedding occurs
        else:
            schedule.append(False)  # No load shedding
            
    return schedule

########### Battery discharge ########### 

def get_battery_discharge_profile(load_profile, pv_output_profile, max_battery_capacity):

    battery_state = 0  # Initial state of the battery

    storage_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy stored in the battery
    discharge_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy discharged from the battery
    curtailed_energies = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the wasted energies
    battery_states = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the battery state
    
    for hour, load in enumerate(load_profile):
        
        net_load = load - pv_output_profile[hour]  # Calculate the net load profile
        
        battery_room = max_battery_capacity - battery_state # Calculate the amount of room left in the battery
        
        energy_stored = 0
        energy_discharged = 0
        curtailed_energy = 0
        
        if net_load < 0:
            # The PV system is producing more energy than the load requires
            # Charge the battery with the excess energy
            energy_stored = min(battery_room, -net_load)
            battery_state = battery_state + energy_stored
            curtailed_energy = -net_load - energy_stored
            
        elif net_load > 0:
            # The PV system is producing less energy than the load requires
            # Discharge the battery to assist with the load 
            energy_discharged = min(battery_state, net_load)
            battery_state = battery_state - energy_discharged
            
        curtailed_energies[hour] = curtailed_energy
        battery_states[hour] = battery_state
        storage_profile[hour] = energy_stored
        discharge_profile[hour] = energy_discharged
        

    return discharge_profile



