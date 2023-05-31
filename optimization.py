from scipy.optimize import minimize
from scipy.optimize import minimize_scalar
from importlib import reload 
import numpy as np 
import economic_analysis
import generate_data
import matplotlib.pyplot as plt


##### CUYRRENT ISSUE IS WHEN I AM RUNNING OPTIMIZATION.PY VS THE DIRECT OPTIMIZATION IN FEASIBLITY ANALYSIS I GET DIFF ANSWERS 
### PROCESS TO FIX: REDUCE OBJECTIVE FUNCTION TO MOST BASIC FORM AND THEN BUILD UP TO SEE WHERE ERORR OCCURS
### ALSO THE MODULES DON'T SEEM TO BE IMOPRTING CORRECTLY (ESPECIALLY TO FEASIBLITY.IPYNB)


def objective_function(x, a):
    
    # Decision variables - PV capacity and Battery capacity 
    pv_capacity = x[0]
    battery_capacity = x[1]
    
    # Capital Cost of Investment 
    pv_capital_cost =  a['additional_pv_capital_cost'] + a['pv_cost_per_kw'] * pv_capacity ** a['pv_cost_exponent']  # (int) capital cost of PV system 
    battery_capital_cost = a['battery_cost_per_kWh'] * battery_capacity ** a['battery_cost_exponent']  # (int) capital cost of battery
    total_capital_cost = pv_capital_cost + battery_capital_cost
    
    # Generate PV Output profile 
    pv_output_profile = generate_data.get_pv_output(a['annual_insolation_profile'], a['pv_efficiency'], pv_capacity) 
    
    # Generate load shedding schedule 
    loadshedding_schedule = generate_data.generate_loadshedding_schedule(a['loadshedding_probability'])
    
    # Generate PV output profile with battery
    pv_with_battery_output_profile = generate_data.simulate_battery_storage(a['load_profile'], pv_output_profile, battery_capacity, a['battery_duration'],
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
    #operational_savings_per_year = 0
    
    # Total 
    cash_flows = [energy_savings_per_year + operational_savings_per_year + carbon_savings_per_year for i in range(a['Rproj'])]

    ##### Calculate NPV #####
    npv = economic_analysis.calculate_npv(total_capital_cost, cash_flows, a['discount_rate'])
    
    return -npv 

def objective_function_with_loadshedding_penalty(x, a):
    
    # Decision variables - PV capacity and Battery capacity 
    pv_capacity = x[0]
    battery_capacity = x[1]
    
    # Capital Cost of Investment 
    # pv_capital_cost =  a['additional_pv_capital_cost'] + a['pv_cost_per_kw'] * pv_capacity ** a['pv_cost_exponent']     # (int) capital cost of PV system 
    # battery_capital_cost = a['battery_cost_per_kWh'] * battery_capacity ** a['battery_cost_exponent'] # (int) capital cost of battery
    # total_capital_cost = pv_capital_cost + battery_capital_cost
    
    total_capital_cost = economic_analysis.calculate_capital_investment(pv_capacity, battery_capacity, a)
    
    #### PAYS Business Model ####
    upfront_payment = a['loan_upfront_adjustment'] * total_capital_cost # (int) upfront payment for panels
    residual_cost_of_panels_owed = total_capital_cost - upfront_payment # (int) residual cost of panels owed

    # Generate PV Output profile 
    pv_output_profile = generate_data.get_pv_output(a['annual_insolation_profile'], a['pv_efficiency'], pv_capacity) 
    
    # Generate load shedding schedule 
    loadshedding_schedule = generate_data.generate_loadshedding_schedule(a['loadshedding_probability'])
    
    # Generate PV output profile with battery
    pv_with_battery_output_profile = generate_data.simulate_battery_storage(a['load_profile'], pv_output_profile, battery_capacity, a['battery_duration'],
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
    
    # Energy  
    energy_savings_per_year = energy_cost_without_pv.sum() - energy_cost_with_pv.sum() # (float) revenue per year from energy savings 
    
    # Operational
    operational_savings_per_year = value_of_charging_saved_by_pv_from_loadshedding.sum() # (float) revenue per year from saved passengers
    
    # Total 
    #cash_flows = [energy_savings_per_year + operational_savings_per_year + carbon_savings_per_year - PAYS_payback for i in range(a['Rproj'])]

    ##### Calculate NPV #####
    # npv = economic_analysis.calculate_npv(total_capital_cost, cash_flows, a['discount_rate'])
    
    npv = economic_analysis.calculate_npv_with_loan(upfront_payment, residual_cost_of_panels_owed, 
                                                    a['loan_payback_period'],
                                                    energy_savings_per_year,
                                                    operational_savings_per_year,
                                                    carbon_savings_per_year, a['discount_rate'], a['Rproj'])
    
    penalty = net_load_affected_by_loadshedding.sum()
    
    npv -= penalty
    
    return -npv 

def objective_function_for_loan(x, a):
    
    # Decision variables - PV capacity and Battery capacity 
    pv_capacity = x[0]
    battery_capacity = x[1]
    
    # Capital Cost of Investment 
    pv_capital_cost =  a['additional_pv_capital_cost'] + a['pv_cost_per_kw'] * pv_capacity ** a['pv_cost_exponent']   # (int) capital cost of PV system 
    battery_capital_cost = a['battery_cost_per_kWh'] * battery_capacity ** a['battery_cost_exponent'] # (int) capital cost of battery
    total_capital_cost = pv_capital_cost + battery_capital_cost
    
    #### PAYS Business Model ####
    upfront_payment = a['loan_upfront_adjustment'] * total_capital_cost # (int) upfront payment for panels
    residual_cost_of_panels_owed = total_capital_cost - upfront_payment # (int) residual cost of panels owed

    # Generate PV Output profile 
    pv_output_profile = generate_data.get_pv_output(a['annual_insolation_profile'], a['pv_efficiency'], pv_capacity) 
    
    # Generate load shedding schedule 
    loadshedding_schedule = generate_data.generate_loadshedding_schedule(a['loadshedding_probability'])
    
    # Generate PV output profile with battery
    pv_with_battery_output_profile = generate_data.simulate_battery_storage(a['load_profile'], pv_output_profile, battery_capacity, a['battery_duration'],
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
    
    # Energy  
    energy_savings_per_year = energy_cost_without_pv.sum() - energy_cost_with_pv.sum() # (float) revenue per year from energy savings 
    
    # Operational
    operational_savings_per_year = value_of_charging_saved_by_pv_from_loadshedding.sum() # (float) revenue per year from saved passengers
    
    # Total 
    #cash_flows = [energy_savings_per_year + operational_savings_per_year + carbon_savings_per_year - PAYS_payback for i in range(a['Rproj'])]

    ##### Calculate NPV #####
    # npv = economic_analysis.calculate_npv(total_capital_cost, cash_flows, a['discount_rate'])
    
    npv = economic_analysis.calculate_npv_with_loan(upfront_payment, residual_cost_of_panels_owed, 
                                                    a['loan_payback_period'],
                                                    energy_savings_per_year,
                                                    operational_savings_per_year,
                                                    carbon_savings_per_year, a['discount_rate'], a['Rproj'])
    
    return -npv 

def objective_function_PAYS(x,a):
    
    # Decision variables - PV capacity and Battery capacity 
    pv_capacity = x[0]
    battery_capacity = x[1]
    
    # Capital Cost of Investment 
    # pv_capital_cost = economic_analysis.calculate_pv_capital_cost(pv_capacity,a)
    # battery_capital_cost = economic_analysis.calculate_battery_capital_cost(battery_capacity,a)
    
    # pv_capital_cost =  a['additional_pv_capital_cost'] + a['pv_cost_per_kw'] * pv_capacity ** a['pv_cost_exponent']    # (int) capital cost of PV system 
    # battery_capital_cost = a['battery_cost_per_kWh'] * battery_capacity ** a['battery_cost_exponent']   # (int) capital cost of battery
    total_capital_cost = economic_analysis.calculate_capital_investment(pv_capacity, battery_capacity, a)
    
    #### PAYS Business Model ####
    upfront_payment = a['PAYS_capital_cost_adjustment'] * total_capital_cost # (int) upfront payment for panels
    residual_cost_of_panels_owed = total_capital_cost - upfront_payment # (int) residual cost of panels owed
    
    # Generate PV Output profile 
    pv_output_profile = generate_data.get_pv_output(a['annual_insolation_profile'], a['pv_efficiency'], pv_capacity) 
    
    # Generate load shedding schedule 
    loadshedding_schedule = generate_data.generate_loadshedding_schedule(a['loadshedding_probability'])
    
    # Generate PV output profile with battery
    pv_with_battery_output_profile = generate_data.simulate_battery_storage(a['load_profile'], pv_output_profile, battery_capacity, a['battery_duration'],
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
    
    # Energy  
    energy_savings_per_year = energy_cost_without_pv.sum() - energy_cost_with_pv.sum() # (float) revenue per year from energy savings 
    
    # Operational
    operational_savings_per_year = value_of_charging_saved_by_pv_from_loadshedding.sum() # (float) revenue per year from saved passengers
    #operational_savings_per_year = 0
    # Total 
    #cash_flows = [energy_savings_per_year + operational_savings_per_year + carbon_savings_per_year for i in range(a['Rproj'])]

    ##### Calculate NPV #####
    npv = economic_analysis.calculate_npv_with_PAYS(upfront_payment, residual_cost_of_panels_owed, a['PAYS_cut_of_savings'], 
                            energy_savings_per_year,
                            operational_savings_per_year,
                           carbon_savings_per_year,
                           a['discount_rate'], a['Rproj'])
    
    return -npv 

def avoid_loadshedding(x, a):
    # Decision variables - PV capacity and Battery capacity 
    pv_capacity = x[0]
    battery_capacity = x[1]
    
    # Generate PV Output profile 
    pv_output_profile = generate_data.get_pv_output(a['annual_insolation_profile'], a['pv_efficiency'], pv_capacity) 
    
    # Generate load shedding schedule 
    loadshedding_schedule = generate_data.generate_loadshedding_schedule(a['loadshedding_probability'])
    
    # Generate PV output profile with battery
    pv_with_battery_output_profile = generate_data.simulate_battery_storage(a['load_profile'], pv_output_profile, battery_capacity, a['battery_duration'],
                                                                            a['battery_charging_efficiency'], a['battery_discharging_efficiency'])
    # Net charging load profile 
    net_load_profile = a['load_profile'] - pv_with_battery_output_profile

    # Find all hours with loadshedding where the net load is positive (i.e. where solar + battery do not provide complete coverage of loadshedding)
    not_covered = [net_load_profile[i] for i, is_shedding in enumerate(loadshedding_schedule) if is_shedding and net_load_profile[i] > 0]

    return -sum(not_covered) # return the number of hours that are not covered by solar + batter


def cover_loadshedding_v2(num_vehicles, vehicle_battery_size):
    '''
    Find the maximum energy capacity of the fleet of vehicles
    '''
    fleet_energy_capacity = num_vehicles * vehicle_battery_size
    
    return fleet_energy_capacity

def plot_sensitivities(sensitivity_var, vals, bounds, initial_guess, a, objective_function):
    
    
    optimal_pv_capacities = []
    optimal_battery_capacities = []
    npvs = []
    
    pv_capital_costs = []
    battery_capital_costs = []
    total_capital_costs = []
    
    for val in vals:
        # Set the value of the sensitivity parameter
        a[sensitivity_var] = val # change the sensitivity variable
        
        # Optimize
        result = minimize(objective_function, x0 = initial_guess, args = (a,), bounds=bounds, method='SLSQP')

        # Extract the optimal capacity
        optimal_pv_capacity = result.x[0]
        optimal_battery_capacity = result.x[1]

        # Calculate the minimum cash flow
        max_npv = -result.fun
        
        # Store results
        optimal_pv_capacities.append(optimal_pv_capacity)
        optimal_battery_capacities.append(optimal_battery_capacity)
        npvs.append(max_npv)
        
        
        # Calculate Capital Cost of Investments 
        pv_capital_cost = optimal_pv_capacity * a['pv_cost_per_kw'] ** 1.2 + a['additional_pv_capital_cost']
        battery_capital_cost = optimal_battery_capacity * a['battery_cost_per_kWh'] ** 1.2
        total_capital_cost = pv_capital_cost + battery_capital_cost
        
        # Store results 
        pv_capital_costs.append(pv_capital_cost)
        battery_capital_costs.append(battery_capital_cost)
        total_capital_costs.append(total_capital_cost)
        
        
    # Plot sensitivities (results)
    fig, ax1 = plt.subplots() 
    ax1.plot(vals, optimal_pv_capacities, label = 'PV Capacity (kW)')
    ax1.plot(vals, optimal_battery_capacities, label = 'Battery Capacity (kWh)')
    ax1.set_xlabel(sensitivity_var)
    ax1.set_ylabel('Capacity')

    ax2 = ax1.twinx()
    ax2.plot(vals, npvs, label = 'NPV', color = 'black')
    ax2.set_ylabel('NPV ($)')

    fig.legend(loc = 'upper right')
    plt.show()
    
    # Plot sensitivities (capital costs)
    plt.plot(vals, pv_capital_costs, label = 'PV Capital Cost')
    plt.plot(vals, battery_capital_costs, label = 'Battery Capital Cost')
    plt.plot(vals, total_capital_costs, label = 'Total Capital Cost')
    plt.xlabel(sensitivity_var)
    plt.ylabel('Capital Cost ($)')
    plt.legend()
    plt.show()
    
    return npvs, optimal_battery_capacities, optimal_pv_capacities, pv_capital_costs, battery_capital_costs, total_capital_costs


def max_number_vehicles():
    
    
    return -num_vehicles