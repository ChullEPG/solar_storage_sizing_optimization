from scipy.optimize import minimize
from scipy.optimize import minimize_scalar
from importlib import reload 
import numpy as np 
import economic_analysis
import generate_data


##### CUYRRENT ISSUE IS WHEN I AM RUNNING OPTIMIZATION.PY VS THE DIRECT OPTIMIZATION IN FEASIBLITY ANALYSIS I GET DIFF ANSWERS 
### PROCESS TO FIX: REDUCE OBJECTIVE FUNCTION TO MOST BASIC FORM AND THEN BUILD UP TO SEE WHERE ERORR OCCURS
### ALSO THE MODULES DON'T SEEM TO BE IMOPRTING CORRECTLY (ESPECIALLY TO FEASIBLITY.IPYNB)


def objective_function(x, a):
    
    # Decision variables - PV capacity and Battery capacity 
    pv_capacity = x[0]
    battery_capacity = x[1]
    
    # Capital Cost of Investment 
    pv_capital_cost =  a['additional_pv_capital_cost'] + a['pv_cost_per_kw'] * pv_capacity ** 1.5   # (int) capital cost of PV system 
    battery_capital_cost = a['battery_cost_per_kWh'] * battery_capacity  # (int) capital cost of battery
    total_capital_cost = pv_capital_cost + battery_capital_cost
    
    # Generate PV Output profile 
    pv_output_profile = generate_data.get_pv_output(a['annual_insolation_profile'], a['pv_efficiency'], pv_capacity) 
    
    # Generate load shedding schedule 
    loadshedding_schedule = generate_data.generate_loadshedding_schedule(a['loadshedding_probability'])
    
    # Generate PV output profile with battery
    #pv_with_battery_output_profile = generate_data.simulate_battery_storage_wip(a['load_profile'], pv_output_profile, 
                                                                             #   battery_capacity, a['battery_duration'])
    
    pv_with_battery_output_profile = generate_data.simulate_battery_storage_v2(a['load_profile'], pv_output_profile, battery_capacity, a['battery_duration'],
                                                                            a['battery_charging_efficiency'], a['battery_discharging_efficiency'])
    # Net charging load profile 
    net_load_profile = a['load_profile'] - pv_with_battery_output_profile

    # Profile of kWh that would be lost to load shedding WITHOUT  solar and battery 
    gross_load_affected_by_loadshedding = np.array([a['load_profile'][i] if is_shedding else 0 for i, is_shedding in enumerate(loadshedding_schedule)])
    
    # Profile of kWh that would have been lost to loadshedding but are saved by the solar + battery generation [these are beneficial, and not to be charged $$ for]
    saved_free_kWh = [min(pv_with_battery_output_profile[i], gross_load_affected_by_loadshedding[i]) if is_shedding else 0 for i, is_shedding in enumerate(loadshedding_schedule)]
    
    # Profile of kWh that would be lost to load shedding WITH solar and battery
    net_load_affected_by_loadshedding = np.array([net_load_profile[i] if is_shedding and net_load_profile[i] > 0 else 0 for i, is_shedding in enumerate(loadshedding_schedule)])
    
    # Find the load profiles that are net of load shedding - this is the load you neeed to charge $ for [in reality you will need an entirely new schedule] 
    gross_load_minus_loadshedding = a['load_profile'] - gross_load_affected_by_loadshedding
    net_load_minus_loadshedding = net_load_profile - net_load_affected_by_loadshedding 
    
    # Value of kWh saved from loadshedding BY solar + battery!  [makes above not needed?]
    value_of_charging_saved_by_pv_from_loadshedding = economic_analysis.get_cost_of_missed_passengers_from_loadshedding(saved_free_kWh, a['cost_per_passenger'],
                                                                                         a['time_passenger_per_kWh'], a['time_periods'])

    # Energy costs ($ for kWh charged) (net of load shedding - so this is actually cheaper than without loadshedding, but we account for the value of missed trips elsewhere)
    energy_cost_without_pv, energy_cost_with_pv = economic_analysis.get_cost_of_charging(gross_load_minus_loadshedding, net_load_minus_loadshedding,
                         a['time_of_use_tariffs'], a['time_periods'], a['feed_in_tariff'], feed_in_tariff_bool = a['feed_in_tariff_bool'])
    
    ##### Monetary savings (revenue) from solar + battery #######
    
    # Carbon
    carbon_savings_per_year = economic_analysis.get_value_of_carbon_offsets(gross_load_minus_loadshedding, net_load_minus_loadshedding, a['grid_carbon_intensity'], a['carbon_price'])
    
    # Enegy  
    energy_savings_per_year = energy_cost_without_pv.sum() - energy_cost_with_pv.sum() # (float) revenue per year from energy savings 
    
    # Operational
    operational_savings_per_year = value_of_charging_saved_by_pv_from_loadshedding.sum() # (float) revenue per year from saved passengers
    
    # Total 
    cash_flows = [energy_savings_per_year + operational_savings_per_year + carbon_savings_per_year for i in range(a['Rproj'])]

    ##### Calculate NPV #####
    npv = economic_analysis.calculate_npv(total_capital_cost, cash_flows, a['discount_rate'])
    
    return -npv 
