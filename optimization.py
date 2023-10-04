# Description: This file contains the objective functions for the optimization problem.
import economic_analysis
import generate_data
import calculations
from tqdm import tqdm
import numpy as np
import pdb
# With loan
def objective_function_with_solar_and_battery_degradation_loan(x, a):
    
    pv_capacity =x[0]
    battery_capacity= x[1] 
    
    # Capital Cost of Investment 
    total_capital_cost = economic_analysis.calculate_capital_cost(pv_capacity, battery_capacity, a)
    # Residual value
    pv_residual_value = a['solar_residual_value_factor'] * a['pv_cost_per_kw'] * pv_capacity 
    battery_residual_value = a['battery_residual_value_factor'] * a['battery_cost_per_kWh'] * battery_capacity
    # Maintenance costs 
    maintenance_costs = (a['pv_annual_maintenance_cost'] * pv_capacity) + (a['battery_annual_maintenance_cost'] * battery_capacity)
    # Battery repurchase cost 
    battery_repurchase_cost = 0
    # Financing
    upfront_payment = a['loan_upfront_adjustment'] * total_capital_cost # (int) upfront payment for panels
    residual_cost_of_panels_owed = (total_capital_cost - upfront_payment) * (1 + a['loan_interest_rate']) # (int) residual cost of panels owed with interest
    
    # Initialize array to hold annual profit streams that will then be discounted according to when they occur in the final NPV calculation
    annual_profits = []
    
    # Initialize total quantity of battery energy throughput
    battery_energy_throughput = 0
    
    # Get max battery energy throughput
    battery_max_energy_throughput = generate_data.get_battery_max_energy_throughput(battery_capacity, a)
    
    for year in tqdm(range(a['Rproj']), desc="Optimizing", ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
        
        # Update PV and battery capacity after degradation   
        usable_pv_capacity = calculations.get_usable_pv_capacity(pv_capacity, year, a) 
        usable_battery_capacity = calculations.get_usable_battery_capacity(battery_capacity, battery_energy_throughput, battery_max_energy_throughput, year, a)
        
        #battery_capacity - (battery_capacity * (battery_energy_throughput / battery_max_energy_throughput) * (1 - a['battery_end_of_life_perc']))
        
        # Generate PV Output profile 
        pv_output_profile = generate_data.get_pv_output(a['annual_capacity_factor'], usable_pv_capacity) 
        
        # Initialize battery repurchae cost and cost of trickle charging
        battery_repurchase_cost = 0
        cost_of_trickle_charging = 0
        

        if battery_energy_throughput < battery_max_energy_throughput: 
            # degrade battery capacity by battery degradation rate
            pv_with_battery_output_profile, battery_throughput, cost_of_trickle_charging = generate_data.simulate_battery_storage_v4(pv_output_profile, usable_battery_capacity,  battery_energy_throughput, battery_max_energy_throughput, a)
            
            battery_energy_throughput = battery_throughput # update battery cycles left
            
        else:
            
            if a['repurchase_battery']: 
                # rebuy cost (discounted)
                battery_repurchase_cost = a['battery_cost_per_kWh'] * battery_capacity / (1 + a['discount_rate']) **year
                # reset usable battery capacity
                usable_battery_capacity = battery_capacity
                # reset battery energy used
                battery_energy_throughput = 0
                
                pv_with_battery_output_profile, battery_throughput, cost_of_trickle_charging = generate_data.simulate_battery_storage_v4(pv_output_profile, battery_capacity, battery_energy_throughput,battery_max_energy_throughput,a)
                
                battery_energy_throughput = battery_throughput
            else:
                pv_with_battery_output_profile = pv_output_profile 
            
        
        # Load profile net of PV and battery production 
        net_load_profile = a['load_profile'] - pv_with_battery_output_profile
        
    
        energy_cost_without_pv, energy_cost_with_pv = economic_analysis.get_cost_of_charging_v2(a['load_profile'], net_load_profile,
                                 a['time_periods'], a['feed_in_tariff'], a['feed_in_tariff_bool'], a)
        
            
        # Energy savings
        energy_savings_per_year = energy_cost_without_pv.sum() - energy_cost_with_pv.sum() # (float) revenue per year from energy savings     
                
        annual_profits.append(energy_savings_per_year - cost_of_trickle_charging - maintenance_costs - battery_repurchase_cost)
        
    
    npv = economic_analysis.calculate_npv_with_loan(upfront_payment, residual_cost_of_panels_owed, 
                                                    annual_profits,
                                                    pv_residual_value, 
                                                    battery_residual_value,
                                                    a)
    
    print("PV capacity:", round(pv_capacity,1))
    print("Battery capacity:", round(battery_capacity,1))
    print("NPV: $", round(npv,1))
    
    return -npv 



# With loan using CRF
def objective_function_with_solar_and_battery_degradation_loan_v2(x, a):
    
    pv_capacity =x[0]
    battery_capacity= x[1] 
    
    # Capital Cost of Investment 
    pv_capital_cost = economic_analysis.calculate_pv_capital_cost(pv_capacity, a, linearize_inverter_cost = a['linearize_inverter_cost'])
    battery_capital_cost = a['battery_cost_per_kWh'] * battery_capacity
    
    ## Annual costs
    loan_installment = (economic_analysis.get_crf(a) * pv_capital_cost) + (economic_analysis.get_crf(a) * battery_capital_cost)
    pv_maintenance_cost = a['pv_annual_maintenance_cost'] * pv_capacity
    battery_maintenance_cost = a['battery_annual_maintenance_cost'] * battery_capacity
    
    
    battery_energy_throughput = 0 # Initialize total quantity of battery energy throughput
    repurchase_battery = a['repurchase_battery'] # Initialize battery repurchase bool 
    battery_max_energy_throughput = generate_data.get_battery_max_energy_throughput(battery_capacity, a) # Get max battery energy throughput
    
    net_cash_flows = [] # Initialize array to hold net cash flows 
    
    for year in tqdm(range(a['Rproj']), desc="Optimizing", ncols=100, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
        
        # Update PV and battery capacity after degradation   
        usable_pv_capacity = calculations.get_usable_pv_capacity(pv_capacity, year, a) 
        usable_battery_capacity = calculations.get_usable_battery_capacity(battery_capacity, battery_energy_throughput, battery_max_energy_throughput, year, a)
                
        # Generate PV Output profile 
        pv_output_profile = generate_data.get_pv_output(a['annual_capacity_factor'], usable_pv_capacity) 
        
        # Initialize battery repurchae cost, residual value, and cost of trickle charging (these are all zero at beginning and change throughout)
        battery_repurchase_cost = 0
        battery_residual_value = 0
        cost_of_trickle_charging = 0
        

        if battery_energy_throughput < battery_max_energy_throughput: 

            pv_with_battery_output_profile, battery_throughput, cost_of_trickle_charging = generate_data.simulate_battery_storage_v4(pv_output_profile, usable_battery_capacity,  battery_energy_throughput, battery_max_energy_throughput, a)
            
            battery_energy_throughput = battery_throughput # update total battery energy throughput 
            
        else:
            if repurchase_battery: 
                battery_repurchase_cost = a['battery_cost_per_kWh'] * battery_capacity / (1 + a['discount_rate'])**year # rebuy cost (discounted)
                battery_residual_value = a['battery_residual_value_factor'] * a['battery_cost_per_kWh'] * battery_capacity

                usable_battery_capacity = battery_capacity # reset usable battery capacity
                battery_energy_throughput = 0 # reset battery energy used
                pv_with_battery_output_profile, battery_throughput, cost_of_trickle_charging = generate_data.simulate_battery_storage_v4(pv_output_profile, battery_capacity, battery_energy_throughput,battery_max_energy_throughput,a)
                battery_energy_throughput = battery_throughput
                if a['limit_battery_repurchases']:
                    repurchase_battery = False
            else:
                pv_with_battery_output_profile = pv_output_profile 
                battery_maintenance_cost = 0
            
        
        # Load profile net of PV and battery production 
        net_load_profile = a['load_profile'] - pv_with_battery_output_profile
        
    
        energy_cost_without_pv, energy_cost_with_pv = economic_analysis.get_cost_of_charging_v2(net_load_profile,  a)
        
        energy_savings_per_year = energy_cost_without_pv.sum() - energy_cost_with_pv.sum() - cost_of_trickle_charging # (float) revenue per year from energy savings     
        maintenance_costs = pv_maintenance_cost + battery_maintenance_cost
        
        net_cash_flows.append(energy_savings_per_year - loan_installment - maintenance_costs - battery_repurchase_cost + battery_residual_value)
        
        #if in final year
        if year == a['Rproj'] - 1:
            # add pv residual value to the last cash flow
            net_cash_flows[-1] += a['solar_residual_value_factor'] * a['pv_cost_per_kw'] * pv_capacity        
    
    npv = economic_analysis.calculate_npv(initial_investment = 0, cash_flows = net_cash_flows, discount_rate = a['discount rate'])
    
    print("PV capacity:", round(pv_capacity,1))
    print("Battery capacity:", round(battery_capacity,1))
    print("NPV: $", round(npv,1))
    
    return -npv 

# With loan using CRF and load shedding overly capability
def objective_function_with_solar_and_battery_degradation_loan_v3(x, a):
    
    pv_capacity = x[0]
    battery_capacity = x[1]
    # Capital Cost of Investment 
    pv_capital_cost = economic_analysis.calculate_pv_capital_cost(pv_capacity, a)
    battery_capital_cost = a['battery_cost_per_kWh'] * battery_capacity
    
    ## Annual costs
    loan_installment = economic_analysis.calculate_crf(a) * (pv_capital_cost + battery_capital_cost)
    pv_maintenance_cost = a['pv_annual_maintenance_cost'] * pv_capacity
    battery_maintenance_cost = a['battery_annual_maintenance_cost'] * battery_capacity
    
    
    battery_energy_throughput = 0 # Initialize total quantity of battery energy throughput
    repurchase_battery = a['repurchase_battery'] # Initialize battery repurchase bool 
    battery_max_energy_throughput = generate_data.get_battery_max_energy_throughput(battery_capacity, a) # Get max battery energy throughput
    
    net_cash_flows = np.zeros(a['Rproj']) # Initialize array to hold net cash flows 
    
    battery_exists = True # true until run out of repurchases
        
    for year in tqdm(range(a['Rproj']), desc="Optimizing", ncols=100, miniters = 0, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", disable = True):
    #for year in range(a['Rproj']):
        
        # Update PV and battery capacity after degradation   
        usable_pv_capacity = calculations.get_usable_pv_capacity(pv_capacity, year, a) 
        
        if battery_exists:
            usable_battery_capacity = calculations.get_usable_battery_capacity(battery_capacity, battery_energy_throughput, battery_max_energy_throughput, year, a)
            
        # Generate PV Output profile 
        pv_output_profile = generate_data.get_pv_output(a['annual_capacity_factor'], usable_pv_capacity) 
        
        # Initialize battery repurchae cost, residual value, and cost of trickle charging (these are all zero at beginning and change throughout)
        battery_repurchase_cost = 0
        battery_residual_value = 0
        cost_of_trickle_charging = 0
            
         ###########################################################################################
          # Battery
          ###########################################################################################  
        
        # Check if the battery is still alive 
        if battery_energy_throughput < battery_max_energy_throughput: 

            pv_with_battery_output_profile, battery_throughput, cost_of_trickle_charging = generate_data.simulate_battery_storage_v4(pv_output_profile, usable_battery_capacity,  battery_energy_throughput, battery_max_energy_throughput, a)
            
            battery_energy_throughput = battery_throughput # update total battery energy throughput 
            
        else:
            if repurchase_battery: 
                battery_repurchase_cost = a['battery_cost_per_kWh'] * battery_capacity / (1 + a['discount rate'])**year # rebuy cost (discounted)
                battery_residual_value = a['battery_residual_value_factor'] * a['battery_cost_per_kWh'] * battery_capacity
                
                years_left = a['Rproj'] - year
                crf_repurchase = (a['interest rate'] * (1 + a['interest rate'])**years_left) / ((1 + a['interest rate'])**years_left - 1)
                loan_installment += crf_repurchase * battery_repurchase_cost

                usable_battery_capacity = battery_capacity # reset usable battery capacity
                battery_energy_throughput = 0 # reset battery energy used
                pv_with_battery_output_profile, battery_throughput, cost_of_trickle_charging = generate_data.simulate_battery_storage_v4(pv_output_profile, battery_capacity, battery_energy_throughput,battery_max_energy_throughput,a)
                battery_energy_throughput = battery_throughput
                if a['limit_battery_repurchases']:
                    repurchase_battery = False
            else:
                pv_with_battery_output_profile = pv_output_profile 
                battery_maintenance_cost = 0
                battery_exists = False
                usable_battery_capacity = 0
                
                

        loadshedding_schedule = a['load_shedding_schedule']
        net_load_profile = a['load_profile'] - pv_with_battery_output_profile
        gross_load_lost_to_loadshedding = np.array([a['load_profile'][i] if is_shedding else 0 for i, is_shedding in enumerate(loadshedding_schedule)])
        
        # Profile of kWh that would have been lost to loadshedding but are saved by the solar + battery generation [these are beneficial, and not to be charged $$ for]
        saved_free_kWh = [min(pv_with_battery_output_profile[i], gross_load_lost_to_loadshedding[i]) if is_shedding else 0 for i, is_shedding in enumerate(loadshedding_schedule)]
        
        # Profile of kWh that would be lost to load shedding WITH solar and battery
        net_load_lost_to_loadshedding = np.array([net_load_profile[i] if is_shedding and net_load_profile[i] > 0 else 0 for i, is_shedding in enumerate(loadshedding_schedule)])
        gross_load_minus_loadshedding = a['load_profile'] - gross_load_lost_to_loadshedding
        net_load_minus_loadshedding = net_load_profile - net_load_lost_to_loadshedding 
        value_of_charging_saved_by_pv_from_loadshedding = economic_analysis.get_cost_of_missed_passengers_from_loadshedding_v2(year, saved_free_kWh, a)
        val_kwh_ls = value_of_charging_saved_by_pv_from_loadshedding.sum()
        
        # if a['full_ev_fleet'] and value_of_charging_saved_by_pv_from_loadshedding.sum() > 0:
        #     val_kwh_ls -= a['hiring_cost'] * net_load_lost_to_loadshedding.sum() * (1/a['kwh_km']) #$/km * kwh * km/kwh = $
        
        load_profile = gross_load_minus_loadshedding
        net_load_profile = net_load_minus_loadshedding  # equals net load profile - 0 if there's no load shedding

                    
        energy_savings = economic_analysis.get_energy_savings(cost_of_trickle_charging, load_profile, net_load_profile, year, a) + val_kwh_ls
        maintenance_costs = (pv_maintenance_cost + battery_maintenance_cost) * (1 + a['inflation rate'])**(year - 1)
        
        net_cash_flows[year] = energy_savings - loan_installment - maintenance_costs - battery_residual_value
        
        
        #if in final year
        if year == a['Rproj'] - 1:
            # add pv residual value to the last cash flow
            net_cash_flows[-1] += a['solar_residual_value_factor'] * a['pv_cost_per_kw'] * pv_capacity        
    
    npv = economic_analysis.calculate_npv(initial_investment = 0, cash_flows = net_cash_flows, discount_rate = a['discount rate'])
    # breakpoint()
    print("PV capacity:", round(pv_capacity))
    print("Battery capacity:", round(battery_capacity))
    print("NPV: $", round(npv))
    
    return -npv 


# Same as V3 but moving back to calendar lifetime for the battery

def objective_function_with_solar_and_battery_degradation_loan_v4(x, a):
    
    pv_capacity = x[0]
    battery_capacity = x[1]
    # Capital Cost of Investment 
    pv_capital_cost = economic_analysis.calculate_pv_capital_cost(pv_capacity, a)
    battery_capital_cost = a['battery_cost_per_kWh'] * battery_capacity
    
    ## Annual costs
    loan_installment = economic_analysis.calculate_crf(a) * (pv_capital_cost + battery_capital_cost)
    pv_maintenance_cost = a['pv_annual_maintenance_cost'] * pv_capacity
    battery_maintenance_cost = a['battery_annual_maintenance_cost'] * battery_capacity
    
    repurchase_battery = a['repurchase_battery'] # Initialize battery repurchase bool 
    net_cash_flows = np.zeros(a['Rproj']) # Initialize array to hold net cash flows 
    
    battery_exists = True # true until run out of repurchases
    
    year_of_battery_lifetime = 0
        
    for year in tqdm(range(a['Rproj']), desc="Optimizing", ncols=100, miniters = 0, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", disable = True):
    #for year in range(a['Rproj']):
        
        # Update PV and battery capacity after degradation   
        usable_pv_capacity = calculations.get_usable_pv_capacity(pv_capacity, year, a) 
        
        if battery_exists:
            annual_deg = (100 * (1 - a['battery_end_of_life_perc']))  / a['battery_lifetime_years'] / 100   # annual degradation rate (%)
            usable_battery_capacity =  battery_capacity * (1 - (annual_deg * year_of_battery_lifetime))
            year_of_battery_lifetime += 1 # update year of battery lifetime
            
        # Generate PV Output profile 
        pv_output_profile = generate_data.get_pv_output(a['annual_capacity_factor'], usable_pv_capacity) 
        
        # Initialize battery repurchae cost, residual value, and cost of trickle charging (these are all zero at beginning and change throughout)
        battery_repurchase_cost = 0
        battery_residual_value = 0
        cost_of_trickle_charging = 0
            
         ###########################################################################################
          # Battery
          ###########################################################################################  
        
        # Check if the battery is still alive 
        if year < a['battery_lifetime_years']:

            pv_with_battery_output_profile, cost_of_trickle_charging = generate_data.simulate_battery_storage_v5(pv_output_profile, usable_battery_capacity, a)
            
            
        else:
            if repurchase_battery: 
                battery_repurchase_cost = a['battery_cost_per_kWh'] * battery_capacity / (1 + a['discount rate'])**year # rebuy cost (discounted)
                battery_residual_value = a['battery_residual_value_factor'] * a['battery_cost_per_kWh'] * battery_capacity
                years_left = a['Rproj'] - year
                crf_repurchase = (a['interest rate'] * (1 + a['interest rate'])**years_left) / ((1 + a['interest rate'])**years_left - 1)
                loan_installment += crf_repurchase * battery_repurchase_cost
                year_of_battery_lifetime = 0
                pv_with_battery_output_profile, cost_of_trickle_charging = generate_data.simulate_battery_storage_v5(pv_output_profile, battery_capacity, a)
                
                if a['limit_battery_repurchases']:
                    repurchase_battery = False
            else:
                pv_with_battery_output_profile = pv_output_profile 
                battery_maintenance_cost = 0
                battery_exists = False
                usable_battery_capacity = 0
                
                

        loadshedding_schedule = a['load_shedding_schedule']
        net_load_profile = a['load_profile'] - pv_with_battery_output_profile
        gross_load_lost_to_loadshedding = np.array([a['load_profile'][i] if is_shedding else 0 for i, is_shedding in enumerate(loadshedding_schedule)])
        
        # Profile of kWh that would have been lost to loadshedding but are saved by the solar + battery generation [these are beneficial, and not to be charged $$ for]
        saved_free_kWh = [min(pv_with_battery_output_profile[i], gross_load_lost_to_loadshedding[i]) if is_shedding else 0 for i, is_shedding in enumerate(loadshedding_schedule)]
        
        # Profile of kWh that would be lost to load shedding WITH solar and battery
        net_load_lost_to_loadshedding = np.array([net_load_profile[i] if is_shedding and net_load_profile[i] > 0 else 0 for i, is_shedding in enumerate(loadshedding_schedule)])
        gross_load_minus_loadshedding = a['load_profile'] - gross_load_lost_to_loadshedding
        net_load_minus_loadshedding = net_load_profile - net_load_lost_to_loadshedding 
        value_of_charging_saved_by_pv_from_loadshedding = economic_analysis.get_cost_of_missed_passengers_from_loadshedding_v2(year, saved_free_kWh, a)
        val_kwh_ls = value_of_charging_saved_by_pv_from_loadshedding.sum()
        
        if a['full_ev_fleet'] and value_of_charging_saved_by_pv_from_loadshedding.sum() > 0:
          # val_kwh_ls -= a['hiring_cost'] * net_load_lost_to_loadshedding.sum() * (1/a['kwh_km']) #$/km * kwh * km/kwh = $
           val_kwh_ls -= (net_load_lost_to_loadshedding.sum() % 100) * 0.2
        
        load_profile = gross_load_minus_loadshedding
        net_load_profile = net_load_minus_loadshedding  # equals net load profile - 0 if there's no load shedding

                    
        energy_savings = economic_analysis.get_energy_savings(cost_of_trickle_charging, load_profile, net_load_profile, year, a) + val_kwh_ls
        maintenance_costs = (pv_maintenance_cost + battery_maintenance_cost) * (1 + a['inflation rate'])**(year - 1)
        
        net_cash_flows[year] = energy_savings - loan_installment - maintenance_costs - battery_residual_value
        
        
        #if in final year
        if year == a['Rproj'] - 1:
            # add pv residual value to the last cash flow
            net_cash_flows[-1] += a['solar_residual_value_factor'] * a['pv_cost_per_kw'] * pv_capacity        
    
    npv = economic_analysis.calculate_npv(initial_investment = 0, cash_flows = net_cash_flows, discount_rate = a['discount rate'])
    # breakpoint()
    print("PV capacity:", round(pv_capacity))
    print("Battery capacity:", round(battery_capacity))
    print("NPV: $", round(npv))
    
    return -npv 














# def objective_function_with_solar_and_battery_degradation_loan_v4(x, a):
    
#     pv_capacity =x[0]
#     battery_capacity= x[1] 
    
#     # Capital Cost of Investment 
#     pv_capital_cost = economic_analysis.calculate_pv_capital_cost(pv_capacity, a)
#     battery_capital_cost = a['battery_cost_per_kWh'] * battery_capacity
    
#     ## Annual costs
#     loan_installment = (economic_analysis.calculate_crf(a) * pv_capital_cost) + (economic_analysis.calculate_crf(a) * battery_capital_cost)
#     pv_maintenance_cost = a['pv_annual_maintenance_cost'] * pv_capacity
#     battery_maintenance_cost = a['battery_annual_maintenance_cost'] * battery_capacity
    
    
#     battery_energy_throughput = 0 # Initialize total quantity of battery energy throughput
#     repurchase_battery = a['repurchase_battery'] # Initialize battery repurchase bool 
#     battery_max_energy_throughput = generate_data.get_battery_max_energy_throughput(battery_capacity, a) # Get max battery energy throughput
    
#     net_cash_flows = [] # Initialize array to hold net cash flows 
    
#     usable_pv_capacities = [pv_capacity * (1 - a['solar_annual_degradation']*year) for year in range(a['Rproj'])]
#     usable_battery_capacities = [battery_capacity * (1 - a['battery_annual_degradation']*year) if year < a['battery_lifetime_years'] else 0 for year in range(a['Rproj'])]
    
        
#     #for year in tqdm(range(a['Rproj']), desc="Optimizing", ncols=100, miniters = 0, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}"):
#     #for year in range(a['Rproj']):
        
    
#     # Generate PV Output profile 
#     pv_output_profiles = generate_data.get_pv_output_vectorized(usable_pv_capacities, a) 

#     # Initialize battery repurchae cost, residual value, and cost of trickle charging (these are all zero at beginning and change throughout)
#     battery_repurchase_cost = 0
#     battery_residual_value = 0
#     cost_of_trickle_charging = 0
            
#         ###########################################################################################
#         # Battery
#         ###########################################################################################  
    
#     # Check if the battery is still alive 


#     pv_with_battery_output_profile, battery_throughput, cost_of_trickle_charging = generate_data.simulate_battery_storage_v4(pv_output_profile, usable_battery_capacity,  battery_energy_throughput, battery_max_energy_throughput, a)
    
#     battery_energy_throughput = battery_throughput # update total battery energy throughput 
        
#     else:
#         if repurchase_battery: 
#             battery_repurchase_cost = a['battery_cost_per_kWh'] * battery_capacity / (1 + a['discount rate'])**year # rebuy cost (discounted)
#             battery_residual_value = a['battery_residual_value_factor'] * a['battery_cost_per_kWh'] * battery_capacity

#             usable_battery_capacity = battery_capacity # reset usable battery capacity
#             battery_energy_throughput = 0 # reset battery energy used
#             pv_with_battery_output_profile, battery_throughput, cost_of_trickle_charging = generate_data.simulate_battery_storage_v4(pv_output_profile, battery_capacity, battery_energy_throughput,battery_max_energy_throughput,a)
#             battery_energy_throughput = battery_throughput
#             if a['limit_battery_repurchases']:
#                 repurchase_battery = False
#         else:
#             pv_with_battery_output_profile = pv_output_profile 
#             battery_maintenance_cost = 0
                
#         ###########################################################################################
#         # Load shedding
#         ###########################################################################################
#         # if a['load_shedding_bool']:
#          # Generate load shedding schedule 
#         loadshedding_schedule = a['load_shedding_schedule']
        
#         # Net charging load profile 
#         net_load_profile = a['load_profile'] - pv_with_battery_output_profile

#         # Profile of kWh that would be lost to load shedding WITHOUT solar and battery 
#         gross_load_lost_to_loadshedding = np.array([a['load_profile'][i] if is_shedding else 0 for i, is_shedding in enumerate(loadshedding_schedule)])
        
#         # Profile of kWh that would have been lost to loadshedding but are saved by the solar + battery generation [these are beneficial, and not to be charged $$ for]
#         saved_free_kWh = [min(pv_with_battery_output_profile[i], gross_load_lost_to_loadshedding[i]) if is_shedding else 0 for i, is_shedding in enumerate(loadshedding_schedule)]
        
#         # Profile of kWh that would be lost to load shedding WITH solar and battery
#         net_load_lost_to_loadshedding = np.array([net_load_profile[i] if is_shedding and net_load_profile[i] > 0 else 0 for i, is_shedding in enumerate(loadshedding_schedule)])
        
#         # Find the load profiles that are net of load shedding - this is the load you neeed to charge $ for [in reality you will need an entirely new schedule] 
#         gross_load_minus_loadshedding = a['load_profile'] - gross_load_lost_to_loadshedding
#         net_load_minus_loadshedding = net_load_profile - net_load_lost_to_loadshedding 
        

#             # Value of kWh saved from loadshedding BY solar + battery!  [makes above not needed?]
#         value_of_charging_saved_by_pv_from_loadshedding = economic_analysis.get_cost_of_missed_passengers_from_loadshedding_v2(year, saved_free_kWh, a)
        
#         load_profile = gross_load_minus_loadshedding
#         net_load_profile = net_load_minus_loadshedding 
#         # else:
#         #     value_of_charging_saved_by_pv_from_loadshedding = np.zeros(1)
#         #     load_profile = a['load_profile']
#         #     net_load_profile = a['load_profile'] - pv_with_battery_output_profile

            
         
        
#         energy_savings = economic_analysis.get_energy_savings(cost_of_trickle_charging, load_profile, net_load_profile, year, a) + value_of_charging_saved_by_pv_from_loadshedding.sum()
#         maintenance_costs = (pv_maintenance_cost + battery_maintenance_cost) * (1 + a['inflation rate'])**(year - 1)
        
#         net_cash_flows.append(energy_savings - loan_installment - maintenance_costs - battery_repurchase_cost + battery_residual_value)
        
        
#         #if in final year
#         if year == a['Rproj'] - 1:
#             # add pv residual value to the last cash flow
#             net_cash_flows[-1] += a['solar_residual_value_factor'] * a['pv_cost_per_kw'] * pv_capacity        
    
#     npv = economic_analysis.calculate_npv(initial_investment = 0, cash_flows = net_cash_flows, discount_rate = a['discount rate'])
#    # breakpoint()
#     print("PV capacity:", round(pv_capacity))
#     print("Battery capacity:", round(battery_capacity))
#     print("NPV: $", round(npv))
    
#     return -npv 