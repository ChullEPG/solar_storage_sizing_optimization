import numpy as np

########### Cost of charging ########### 

def cost_of_charging(load_profile, pv_output_profile, energy_usage_cost):
    
    net_load_profile = load_profile - pv_output_profile # (list) charging load in each hour of the yaer net of solar PV output 

    net_load_profile = np.array(net_load_profile, dtype=int)
   # Initialize total cost variables
    cost_no_pv = []
    cost_with_pv =  []
    
    # Calculate total cost of energy with and without PV

    for i in range(len(load_profile)):
        cost_no_pv.append(load_profile[i] * energy_usage_cost)
        cost_with_pv.append(net_load_profile[i] * energy_usage_cost)
            
    # Convert cost_no_pv and cost_with_pv to numpy arrays
    cost_no_pv = np.array(cost_no_pv)
    cost_with_pv = np.array(cost_with_pv)
    
    return cost_no_pv, cost_with_pv 

########### NPV ########### 

def calculate_npv(initial_investment, cash_flows, discount_rate):
    values = []
    for idx, cash_flow in enumerate(cash_flows):
        this_year_value = cash_flow /(1 + discount_rate)**idx
        values.append(this_year_value)
    total_benefits = sum(values)
    total_costs = initial_investment
    npv = total_benefits - total_costs
    return total_benefits, total_costs, npv


########### Cost of loadshedding ########### 

def get_cost_of_missed_passengers_from_loadshedding(kWh_affected_by_loadshedding: list,
                                                     cost_per_passenger: float,
                                                     time_passenger_per_kWh: float, 
                                                     time_periods: dict):

    # Obtain energy costs for each time period of the day
    morning_passenger_per_kWh = time_passenger_per_kWh['morning'] # (float) number of passengers per kWh in the morning
    afternoon_passenger_per_kWh= time_passenger_per_kWh['afternoon']
    evening_passenger_per_kWh = time_passenger_per_kWh['evening']
    night_passenger_per_kWh = time_passenger_per_kWh['night']
    
    # Obtain time periods for each time period of the day
    morning_start = time_periods['morning_start']
    afternoon_start = time_periods['afternoon_start']
    evening_start = time_periods['evening_start']
    night_start = time_periods['night_start']
    
    # Initialize total cost variables
    passengers_missed = np.zeros(len(kWh_affected_by_loadshedding))
    
    # Calculate total cost of energy with and without PV

    for hour, kWh in enumerate(kWh_affected_by_loadshedding):
        
        curr_hour_of_day = i % 24
        
        if morning_start <= curr_hour_of_day < afternoon_start:
            passengers_missed[hour] = kWh * morning_passenger_per_kWh

        elif afternoon_start <= curr_hour_of_day < evening_start:
            passengers_missed[hour] = kWh * afternoon_passenger_per_kWh
                
        elif evening_start <= curr_hour_of_day < night_start:
            passengers_missed[hour] = kWh * evening_passenger_per_kWh
            
        else:
            passengers_missed[hour] = kWh * night_passenger_per_kWh
            
    return passengers_missed * cost_per_passenger




########### Carbon offsets ########### 

def get_value_of_carbon_offsets(load_profile, net_load_profile, grid_carbon_intensity, carbon_price):
    carbon_cost_gross_load = load_profile.sum() * grid_carbon_intensity *  carbon_price  # kWh * kgCO2/kWh * $/kgCO2 = $
    carbon_cost_net_load = net_load_profile.sum() * grid_carbon_intensity *  carbon_price  # kWh * kgCO2/kWh * $/kgCO2 = $ 
    return carbon_cost_gross_load - carbon_cost_net_load