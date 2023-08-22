import numpy as np
import matplotlib.pyplot as plt
import datetime
import pysolar.solar as solar
import random
import math 

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
                             charging_power,
                             plot = True):
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
    for i in range(num_vehicles):
        for day in range(total_days):
            start_time = start_times[i, day]
            duration = durations[i, day]
            end_time = start_time + duration

            # Calculate the charging load during the charging period
            mask = (time >= start_time) & (time < end_time)
            load_profile[mask] += charging_power
    if plot: 
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

def get_pv_output(capacity_factor, insolation_profile, pv_efficiency, renewables_ninja, pv_capacity):
    '''
    This function obtains the solar PV output profile given a solar insolation profile, PV efficiency, and PV capacity. The function returns the PV output profile.'''
    if renewables_ninja:
        pv_output_profile = [pv_capacity * cf  for cf in capacity_factor]
        
    else:
        # Calculate daily PV output profile
        pv_output_profile = [pv_capacity * pv_efficiency * insolation / 1000 for insolation in insolation_profile]

    
    return pv_output_profile


def get_pv_output_over_project_lifetime(capacity_factor, insolation_profile, pv_efficiency, renewables_ninja, pv_capacity, a):
    '''
    This functiopvn obtains the solar PV output profile given a solar insolation profile, PV efficiency, and PV capacity. The function returns the PV output profile.
    '''
    pv_output_profile = []
    
    if renewables_ninja:
        for year in range(a['Rproj']):
            pv_capacity = pv_capacity * (1 - a['solar_annual_degradation'])**year 
            this_year_pv_output_profile = [pv_capacity * cf  for cf in capacity_factor]
            pv_output_profile.append(this_year_pv_output_profile)
    else:
        # Calculate daily PV output profile
        for year in range(a['Rproj']):
            pv_capacity = pv_capacity * (1 - a['solar_annual_degradation'])**year 
            this_year_pv_output_profile = [pv_capacity * pv_efficiency * insolation / 1000 for insolation in insolation_profile]
            pv_output_profile.append(this_year_pv_output_profile)
    # flatten list
    pv_output_profile = [item for sublist in pv_output_profile for item in sublist]
    
    return pv_output_profile

# PV Output with battery storage
def simulate_battery_storage(load_profile, pv_output_profile, 
                             battery_capacity_total, battery_duration,
                             charging_efficiency, discharging_efficiency,
                             depth_of_discharge, max_cycles):
    
    battery_capacity = depth_of_discharge * battery_capacity_total # Calculate the amount of battery capacity that can be used
    
    battery_power_rating = battery_capacity_total / battery_duration # Calculate the power rating of the battery
    
    battery_state = 0  # Initial state of the battery

    battery_states = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the battery state
        
    
    # Taken
    battery_storage_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy stored in the battery
    battery_discharge_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy discharged from the battery

    # Losses 
    losses_from_efficiency = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the wasted energies
    losses_from_curtailment = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the wasted energies
    
    # Useful 
    battery_energy_draw_from_pv_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy discharged from the battery
    load_energy_received_from_battery_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy discharged from the battery
    load_profile = list(load_profile)
    net_load_profile = [load - pv for load,pv in zip(load_profile ,pv_output_profile)] # Calculate the net load profile

    for hour, net_load in enumerate(net_load_profile):  
               
        battery_room = battery_capacity - battery_state # Calculate the amount of room left in the battery
        
        # Taken in each time step
        energy_stored_in_battery = 0
        energy_discharged_from_battery = 0

        # Losses in each time step 
        loss_from_efficiency = 0
        loss_from_curtailment = 0
        
        # Useful in each time step (contributes to PV profile)
        energy_drawn_from_pv = 0
        energy_received_by_load = 0
        
        if net_load < 0:
            # The PV system is producing more energy than the load requires
            # Charge the battery with the excess energy
            energy_drawn_from_pv = min(battery_room/charging_efficiency, abs(net_load), battery_power_rating) # take -net_load for abs vale
            
            # Actual energy stored in battery is subject to charging efficiency
            energy_stored_in_battery = energy_drawn_from_pv * charging_efficiency
            
            # Update battery state 
            battery_state = battery_state + energy_stored_in_battery
            
            # Losses 
            loss_from_efficiency = energy_drawn_from_pv - energy_stored_in_battery
            loss_from_curtailment = -net_load - energy_drawn_from_pv
            
        elif net_load >= 0:
            # The PV system is producing less energy than the load requires
            # Discharge the battery to assist with the load
            energy_discharged_from_battery = min(battery_state, net_load/discharging_efficiency, battery_power_rating)  
            
            # Actual energy received by load is subject to discharging efficiency
            energy_received_by_load = energy_discharged_from_battery * discharging_efficiency
            
            # Update battery state 
            battery_state = battery_state - energy_discharged_from_battery
            
            # Losses
            loss_from_efficiency = energy_discharged_from_battery - energy_received_by_load
            loss_from_curtailment = 0
            

        battery_states[hour] = battery_state

        # Taken
        battery_storage_profile[hour] = energy_stored_in_battery
        battery_discharge_profile[hour] = energy_discharged_from_battery
        
        # Losses
        losses_from_efficiency[hour] = loss_from_efficiency
        losses_from_curtailment[hour] = loss_from_curtailment
        
        # Useful 
        battery_energy_draw_from_pv_profile[hour] = energy_drawn_from_pv
        load_energy_received_from_battery_profile[hour] = energy_received_by_load

        
    pv_with_battery_output_profile = pv_output_profile + load_energy_received_from_battery_profile - battery_energy_draw_from_pv_profile
    
    
    return pv_with_battery_output_profile

# PV Output with battery storage
def simulate_battery_storage_v2(load_profile, pv_output_profile, 
                             battery_capacity_total, battery_duration,
                             charging_efficiency, discharging_efficiency,
                             depth_of_discharge, max_cycles):
    
    battery_capacity = depth_of_discharge * battery_capacity_total # Calculate the amount of battery capacity that can be used
    
    battery_power_rating = battery_capacity_total / battery_duration # Calculate the power rating of the battery
    
    battery_state = 0  # Initial state of the battery

    battery_states = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the battery state
    
    num_cycles = 0 # Keep track of the number of cycles the battery has done
    
    
    # Taken
    battery_storage_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy stored in the battery
    battery_discharge_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy discharged from the battery

    # Losses 
    losses_from_efficiency = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the wasted energies
    losses_from_curtailment = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the wasted energies
    
    # Useful 
    battery_energy_draw_from_pv_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy discharged from the battery
    load_energy_received_from_battery_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy discharged from the battery
    load_profile = list(load_profile)
    net_load_profile = [load - pv for load,pv in zip(load_profile ,pv_output_profile)] # Calculate the net load profile

    for hour, net_load in enumerate(net_load_profile): 
        
        if num_cycles < max_cycles: 
            #net_load = load - pv_output_profile[hour]  # Calculate the net load profile
            
            battery_room = battery_capacity - battery_state # Calculate the amount of room left in the battery
            
            # Taken 
            energy_stored_in_battery = 0
            energy_discharged_from_battery = 0

            # Losses
            loss_from_efficiency = 0
            loss_from_curtailment = 0
            
            # Useful
            energy_drawn_from_pv = 0
            energy_received_by_load = 0
            
            if net_load < 0:
                # The PV system is producing more energy than the load requires
                # Charge the battery with the excess energy
                energy_drawn_from_pv = min(battery_room/charging_efficiency, -net_load, battery_power_rating)
                energy_stored_in_battery = energy_drawn_from_pv * charging_efficiency
                
                # Update battery state 
                battery_state = battery_state + energy_stored_in_battery
                
                # Losses 
                loss_from_efficiency = energy_drawn_from_pv - energy_stored_in_battery
                loss_from_curtailment = -net_load - energy_drawn_from_pv
                
            elif net_load >= 0:
                # The PV system is producing less energy than the load requires
                # Discharge the battery to assist with the load
                energy_discharged_from_battery = min(battery_state, net_load/discharging_efficiency, battery_power_rating)  
                
                if energy_discharged_from_battery > 0:
                    num_cycles +=  1
                    
                energy_received_by_load = energy_discharged_from_battery * discharging_efficiency
                
                # Update battery state 
                battery_state = battery_state - energy_discharged_from_battery
                
                # Losses
                loss_from_efficiency = energy_discharged_from_battery - energy_received_by_load
                loss_from_curtailment = 0
                

            battery_states[hour] = battery_state

            # Taken
            battery_storage_profile[hour] = energy_stored_in_battery
            battery_discharge_profile[hour] = energy_discharged_from_battery
            
            # Losses
            losses_from_efficiency[hour] = loss_from_efficiency
            losses_from_curtailment[hour] = loss_from_curtailment
            
            # Useful 
            battery_energy_draw_from_pv_profile[hour] = energy_drawn_from_pv
            load_energy_received_from_battery_profile[hour] = energy_received_by_load
        else: # if there are no cycles left
            break
        
    pv_with_battery_output_profile = pv_output_profile + load_energy_received_from_battery_profile - battery_energy_draw_from_pv_profile
    
    num_cycles_left = max_cycles - num_cycles
    
    
    return pv_with_battery_output_profile, num_cycles_left

def simulate_battery_storage_v3(pv_output_profile, battery_capacity_total, battery_energy_throughput, battery_max_energy_throughput, a):
    
    battery_capacity = a['depth_of_discharge'] * battery_capacity_total # Calculate the amount of battery capacity that can be used
    
    battery_power_rating = battery_capacity_total / a['battery_duration'] # Calculate the power rating of the battery
    
    battery_state = 0  # Initial state of the battery

    battery_states = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the battery state
        
    
    # Taken
    battery_storage_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy stored in the battery
    battery_discharge_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy discharged from the battery

    # Losses 
    losses_from_efficiency = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the wasted energies
    losses_from_curtailment = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the wasted energies
    
    # Useful 
    battery_energy_draw_from_pv_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy discharged from the battery
    load_energy_received_from_battery_profile = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the energy discharged from the battery
    load_profile = list(a['load_profile'])
    net_load_profile = [load - pv for load,pv in zip(load_profile ,pv_output_profile)] # Calculate the net load profile
    
    charging_efficiency = a['battery_charging_efficiency']
    discharging_efficiency = a['battery_discharging_efficiency']

    for hour, net_load in enumerate(net_load_profile): 
        
        if battery_energy_throughput < a['battery_max_energy_throughput']: # if haven't exceededm maximum energy throughput for the battery
            
            battery_room = battery_capacity - battery_state # Calculate the amount of room left in the battery
            
            # Taken 
            energy_stored_in_battery = 0
            energy_discharged_from_battery = 0

            # Losses
            loss_from_efficiency = 0
            loss_from_curtailment = 0
            
            # Useful
            energy_drawn_from_pv = 0
            energy_received_by_load = 0
            
            if net_load < 0:
                # The PV system is producing more energy than the load requires
                # Charge the battery with the excess energy
                energy_drawn_from_pv = min(battery_room/charging_efficiency, -net_load, battery_power_rating)
                energy_stored_in_battery = energy_drawn_from_pv * charging_efficiency
                
                # Update battery state 
                battery_state = battery_state + energy_stored_in_battery
                
                # Losses 
                loss_from_efficiency = energy_drawn_from_pv - energy_stored_in_battery
                loss_from_curtailment = -net_load - energy_drawn_from_pv
                
                # Update battery energy throughput 
                battery_energy_throughput += energy_stored_in_battery
                
            elif net_load >= 0:
                # The PV system is producing less energy than the load requires
                # Discharge the battery to assist with the load
                energy_discharged_from_battery = min(battery_state, net_load/discharging_efficiency, battery_power_rating)  
                
                    
                energy_received_by_load = energy_discharged_from_battery * discharging_efficiency
                
                # Update battery state 
                battery_state = battery_state - energy_discharged_from_battery
                
                # Losses
                loss_from_efficiency = energy_discharged_from_battery - energy_received_by_load
                loss_from_curtailment = 0
                

            battery_states[hour] = battery_state

            # Taken
            battery_storage_profile[hour] = energy_stored_in_battery
            battery_discharge_profile[hour] = energy_discharged_from_battery
            
            # Losses
            losses_from_efficiency[hour] = loss_from_efficiency
            losses_from_curtailment[hour] = loss_from_curtailment
            
            # Useful 
            battery_energy_draw_from_pv_profile[hour] = energy_drawn_from_pv
            load_energy_received_from_battery_profile[hour] = energy_received_by_load
        else: # if there are no cycles left
            break
        
    pv_with_battery_output_profile = pv_output_profile + load_energy_received_from_battery_profile - battery_energy_draw_from_pv_profile
    
        
    return pv_with_battery_output_profile, battery_energy_throughput


def simulate_battery_storage_v4(pv_output_profile, battery_capacity_total, battery_energy_throughput, battery_max_energy_throughput, a):
    
    # Net load profile
    net_load_profile = [load - pv for load,pv in zip(list(a['load_profile']),pv_output_profile)] # Calculate the net load profile
    
    # Usable battery capacity
    battery_capacity_usable = a['depth_of_discharge'] * battery_capacity_total # Calculate the amount of battery capacity that can be used
    
    # Max kWh charge or discharge in an hour (c-rating proxy)
    battery_power_rating = battery_capacity_total / a['battery_duration'] 
    
    # Initial energy stored in battery
    battery_current_energy = 0  
    
    # Keep track of total energy moved by the battery 
    battery_energy_draw_from_pv_profile = np.zeros(len(pv_output_profile)) # Energy taken from PV to battery (gross of charging efficiency)
    load_energy_received_from_battery_profile = np.zeros(len(pv_output_profile)) # Energy received by EVs from battery (net of discharging efficiency)
    
    
    # Costs
    cost_of_trickle_charging = np.zeros(len(pv_output_profile))
    
    for hour, net_load in enumerate(net_load_profile): 
        
        if battery_energy_throughput < battery_max_energy_throughput: # if haven't exceededm maximum energy throughput for the battery
            
            # Update the amount of room (capacity) available in the battery
            battery_room = battery_capacity_usable - battery_current_energy 
            
            # Update state of charge
            state_of_charge = 100 * (battery_current_energy/battery_capacity_total)
            
            
            # Charging efficiency changes at high levels of charge
            if state_of_charge <= 85 :
                curr_charge_efficiency = a['battery_charging_efficiency']
            else:
                curr_charge_efficiency = a['battery_charging_efficiency'] * battery_current_energy
                curr_charge_efficiency = (1 - math.exp((state_of_charge-85)/4)/120) #TODO: Chat with Brendan to get the actual equation
            
            # Taken energy
            energy_stored_in_battery = 0 
            energy_discharged_from_battery = 0
            
            # Useful energy
            energy_drawn_from_pv = 0
            energy_received_by_load = 0
            
            if net_load < 0: # Excess PV production
                
                # Total energy drawn from PV into battery. (limited by room left in the battery, net load available, and battery c-rating,)
                energy_drawn_from_pv = min(battery_room/curr_charge_efficiency, abs(net_load), battery_power_rating)
                
                # Net energy stored in battery
                energy_stored_in_battery = energy_drawn_from_pv * curr_charge_efficiency

                # Update battery state 
                battery_current_energy = battery_current_energy + energy_stored_in_battery
        
            
            elif net_load > 0: # Excess EV Load
                
                # Total energy discharged from battery. (limited by energy available in battery, energy demand, and battery c-rating)
                energy_discharged_from_battery = min(battery_current_energy, net_load/a['battery_discharging_efficiency'], battery_power_rating)  
                
                # Net energy received by EVs
                energy_received_by_load = energy_discharged_from_battery * a['battery_discharging_efficiency']
                
                # Update battery state 
                battery_current_energy = battery_current_energy - energy_discharged_from_battery
                      
            elif net_load == 0: 
                if a['enable_trickle_charging']:
                    if ((hour % 24) < 5) or ((hour % 24) > 20): # Charge from grid only in off-peak times
                        
                        # Total energy drawn from grid (limited by trickle charging rate and room available in battery)
                        energy_drawn_from_grid = min(a['battery_trickle_charging_rate'], battery_room/curr_charge_efficiency)
                        
                        # Net energy stored in battery
                        energy_stored_in_battery = energy_drawn_from_grid * curr_charge_efficiency
                        
                        # Electricity price based on season
                        if (hour > a['high_period_start']) & (hour <= a['high_period_end']): # high period (all peak)
                            elec_price = a['time_of_use_tariffs_high']['off_peak']
                        else:
                            elec_price = a['time_of_use_tariffs_low']['off_peak']
                            
                        # Cost of electricity drawn
                        cost_of_charging = elec_price * energy_drawn_from_grid 
                        
                
            # Update battery energy throughput 
            battery_energy_throughput += energy_stored_in_battery
            
            # Useful 
            battery_energy_draw_from_pv_profile[hour] = energy_drawn_from_pv
            load_energy_received_from_battery_profile[hour] = energy_received_by_load
            
            # Cost 
            cost_of_trickle_charging[hour] = max(cost_of_charging, 0)
             
        else: # if there are no cycles left
            break
        
    pv_with_battery_output_profile = pv_output_profile + load_energy_received_from_battery_profile - battery_energy_draw_from_pv_profile
    
        
    return pv_with_battery_output_profile, battery_energy_throughput, cost_of_trickle_charging.sum()


########### Loadshedding ########### 


def get_battery_max_energy_throughput(battery_capacity, a):
    # Separating out this calculation to make it readable in case I return later and can't remember how is calculated. TODO: check this is right :) 
    usable_battery_capacity = battery_capacity * a['depth_of_discharge']
    round_trip_efficiency = a['battery_charging_efficiency'] * a['battery_discharging_efficiency']
    return (a['battery_max_cycles'] * usable_battery_capacity * round_trip_efficiency)
    
    



def generate_loadshedding_schedule(pv_output_profile, loadshedding_probability, set_random_seed = True):
    ''' 
    Generates loadshedding schedulef from average annual loadshedding probability [requires 1 value]
    '''
    schedule = []
    hours_in_project_lifetime = len(pv_output_profile) # Calculate the number of hours of the project lifetime
    
    #set random seed
    if set_random_seed:
        random.seed(0)
    
    for _ in range(hours_in_project_lifetime):
        # Generate a random value between 0 and 1
        random_value = random.random()
        
        # Determine if load shedding occurs based on the random value
        # Adjust the threshold value to control the frequency of load shedding
        if random_value < loadshedding_probability:
            schedule.append(True)  # Load shedding occurs
        else:
            schedule.append(False)  # No load shedding
            
    return schedule
########### Loadshedding ########### 

def generate_loadshedding_schedule(pv_output_profile, loadshedding_probability, set_random_seed = True):
    ''' 
    Generates loadshedding schedulef from average annual loadshedding probability [requires 1 value]
    '''
    schedule = []
    hours_in_project_lifetime = len(pv_output_profile) # Calculate the number of hours of the project lifetime
    
    #set random seed
    if set_random_seed:
        random.seed(0)
    
    for _ in range(hours_in_project_lifetime):
        # Generate a random value between 0 and 1
        random_value = random.random()
        
        # Determine if load shedding occurs based on the random value
        # Adjust the threshold value to control the frequency of load shedding
        if random_value < loadshedding_probability:
            schedule.append(True)  # Load shedding occurs
        else:
            schedule.append(False)  # No load shedding
            
    return schedule


def generate_stochastic_loadshedding_schedule(shedding_profile, set_random_seed = False):
    '''
    Generates loadshedding schedule from hourly probabiilty profile [requires 24 values]
    '''
    if set_random_seed:
        random.seed(0)
        
    hours_in_year = 365 * 24
    load_shedding_schedule = []
    
    for hour in range(hours_in_year):
        curr_hour = hour % 24
        prob = shedding_profile[curr_hour]
        shedding = 1 if random.random() < prob else 0
        load_shedding_schedule.append(shedding)
    
    return load_shedding_schedule




########### Battery discharge ########### 

def get_battery_discharge_profile(load_profile, pv_output_profile, max_battery_capacity):

    battery_current_state = 0  # Initial state of the battery

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



