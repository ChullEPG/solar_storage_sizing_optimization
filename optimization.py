# Description: This file contains the objective functions for the optimization problem.
import economic_analysis
import generate_data
import calculations
from tqdm import tqdm
import numpy as np
import pdb


# Battery: calendar lifetime, linear degradation

def objective_function(x, a):
    
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
           val_kwh_ls -= net_load_lost_to_loadshedding.sum() * (1/a['kwh_km']) * 0.016 #without extra hiring cost
        
        
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
    print("val kWh LS:", round(val_kwh_ls))
    
    return -npv 


# saem as v4 but with "incremental" fleet electrification

def objective_function_with_incremental_fleet_electrification(x, a):
    
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
        
        #incrementally increase load profile
        if year > 5 and year <= 10: 
            a['load_profile'] = a['load_profile_2']
        elif year > 10 and year <= 15:
            a['load_profile'] = a['load_profile_3']
        elif year >= 15:
            a['load_profile'] = a['load_profile_4']
           # a['full_ev_fleet'] = True # Hiring cost activated
            
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
           val_kwh_ls -= (net_load_lost_to_loadshedding.sum()) * (1/a['kwh_km']) * 0.15 * 1.05 #without extra hiring cost
        
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




