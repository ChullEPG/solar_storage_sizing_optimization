import numpy as np
import calculations
import generate_data
########### NPV ########### 

def calculate_npv_old(initial_investment, cash_flows, discount_rate):
    
    values = []
    for idx, cash_flow in enumerate(cash_flows):
        this_year_value = cash_flow /(1 + discount_rate)**idx
        values.append(this_year_value)
            
    total_benefits = sum(values)
    total_costs = initial_investment
    npv = total_benefits - total_costs 
    return npv


def calculate_npv(initial_investment, cash_flows, discount_rate):
    present_values = [cf / (1 + discount_rate) ** idx for idx, cf in enumerate(cash_flows)]
    npv = sum(present_values) - initial_investment
    return npv


def calculate_npv_with_loan(initial_investment, residual_cost_of_panels_owed,  
                            revenues,
                           pv_residual_value,
                           battery_residual_value,
                           a):
    
    # Payback  - assume that the loan is paid back in equal installments over the loan_payback_period (interest already added in optimization function)
    installments = (residual_cost_of_panels_owed / a['loan_payback_period']) 
    
    costs = np.zeros(len(revenues))
    # Fill the first num_periods elements of costs with loan_payback_per_period
    costs[:a['loan_payback_period']] = installments
    
    cash_flows = [revenue - cost for revenue,cost in zip(revenues,costs)]
    
    values = []
    for idx, cash_flow in enumerate(cash_flows):
        this_year_value = cash_flow /(1 + a['discount_rate'])**idx
        values.append(this_year_value)
        # add residual value in final year
        if idx == len(cash_flows) - 1:
            # add residual value (discounted)
            residual_value = (pv_residual_value + battery_residual_value) / (1 + a['discount_rate'])**idx
            values.append(residual_value)
        
    npv = sum(values) - initial_investment
        
    return npv 


def calculate_npv_with_PAYS(initial_investment, residual_cost_of_panels_owed,  
                            energy_savings,
                            other_revenues,
                           pv_residual_value,
                           battery_residual_value,
                           a):
    
    # Payback per period 
    installments = [es * a['PAYS_cut_of_savings'] for es in energy_savings]
    
    # Energy savings that are left over after paying back the loan
    energy_savings_kept = [es * (1 - a['PAYS_cut_of_savings']) for es in energy_savings]
    
    # Total revenues
    revenues = other_revenues + energy_savings_kept
    
    # Find how many installments are needed to pay off the panels
    for idx, installment in enumerate(installments):
        residual_cost_of_panels_owed -= installment
        if residual_cost_of_panels_owed < 0: 
            installments[idx] = installment + residual_cost_of_panels_owed # reset the last installment to be only what is left of the residual cost of panels owed
            installments[idx:] = [0] * (len(installments) - idx) # no more installments owed 
            break
    
        
        
    
    # # Costs each period - max b/t installments and "loan amont" ensure the panels are paid off in the lifetime of the panels
    # #payback_per_period = max(installments, residual_cost_of_panels_owed/a['Rproj'])
    # payback_per_period = installments 
    
    # if payback_per_period == residual_cost_of_panels_owed/a['Rproj']:
    #     num_periods = a['Rproj']
    # else: 
    #     num_periods = 0
    #     paid_back = 0
    #     while paid_back < residual_cost_of_panels_owed:
    #         paid_back += payback_per_period
    #         num_periods += 1 
        
    costs = installments

    cash_flows = [revenue - cost for revenue,cost in zip(revenues,costs)]
    if residual_cost_of_panels_owed > 0:
        # subtract it from the last cash flow (pay back the rest of what is owed in the final time period)
        cash_flows[-1] -= residual_cost_of_panels_owed
    
    values = []
    for idx, cash_flow in enumerate(cash_flows):
        this_year_value = cash_flow /(1 + a['discount_rate'])**idx
        values.append(this_year_value)
        if idx == len(cash_flows) - 1:
            # add residual value (discounted)
            residual_value = (pv_residual_value + battery_residual_value) / (1 + a['discount_rate'])**idx
            values.append(residual_value)
            
    npv = sum(values) - initial_investment
        
    return npv 


########## Investment Cost ############

# def calculate_capital_investment(pv_capacity, battery_capacity, a):
#     # Capital Cost of Investment 
#     pv_capital_cost =  a['additional_pv_capital_cost'] + a['pv_cost_per_kw'] * pv_capacity #** a['pv_cost_exponent']     # (int) capital cost of PV system 
#     battery_capital_cost = a['battery_cost_per_kWh'] * battery_capacity #** a['battery_cost_exponent'] # (int) capital cost of battery
#     total_capital_cost = pv_capital_cost + battery_capital_cost
    
#     return total_capital_cost

def calculate_pv_capital_cost(pv_capacity, a):
    
    # find the inverter cost using a['inverter_cost_schedule'] and the pv_capacity 
    # to do so, must find the closest pv capacity in the schedule
    
    # if linearize_inverter_cost:
    inverter_cost = pv_capacity * a['inverter_cost_per_kw'] 
        
    # else:  # Use cost schedule
    #     pv_capacities = a['inverter_cost_schedule'].keys()
    #     closest_pv_capacity = min(pv_capacities, key=lambda x:abs(x-pv_capacity))
    #     inverter_cost = a['inverter_cost_schedule'][closest_pv_capacity]
        
    panel_cost = a['pv_cost_per_kw'] * pv_capacity 

    # Components cost
    component_cost = panel_cost + inverter_cost # $/kW

    # Other costs
    peripherals_cost = component_cost * 0.20 # $/kW
    installation_cost = (component_cost + peripherals_cost) * 0.10 # $/kW
    markup_cost = (component_cost + peripherals_cost + installation_cost) * 0.33 # $/kW
    
    total_pv_capital_cost = component_cost + peripherals_cost + installation_cost + markup_cost
    
    return total_pv_capital_cost

def calculate_crf(a):
    # Calculate annual payments   
    return (a['interest rate'] * (1 + a['interest rate'])**a['Rproj']) / ((1 + a['interest rate'])**a['Rproj'] - 1)


def get_batt_net_present_cost(pv_capacity, battery_capacity, a):
   
    battery_capital_cost = a['battery_cost_per_kWh'] * battery_capacity
    loan_installment = calculate_crf(a) * (battery_capital_cost)
    battery_maintenance_cost = a['battery_annual_maintenance_cost'] * battery_capacity
    repurchase_battery = a['repurchase_battery']
    battery_exists = True 
    npc = 0
    year_of_battery_lifetime =0

    for year in range(a['Rproj']):
        
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
                
        npc +=  (loan_installment + battery_maintenance_cost - battery_residual_value + cost_of_trickle_charging)/((1 + a['discount rate']) ** year)

    
    return npc # lcoe


def get_pv_net_present_cost(pv_capacity, a):
    npc = 0
    pv_capital_cost = calculate_pv_capital_cost(pv_capacity, a)
    loan_installment = calculate_crf(a) * (pv_capital_cost) 
    
    pv_maintenance_cost = a['pv_annual_maintenance_cost'] * pv_capacity

    for year in range(a['Rproj']):
        npc += (loan_installment + pv_maintenance_cost)/((1 + a['discount rate'])**year)
        if year == a['Rproj'] - 1:
            npc -= (a['solar_residual_value_factor'] * a['pv_cost_per_kw'] * pv_capacity)/((1 + a['discount rate'])**year)
            
    return npc    

def get_energy_served_by_pv(pv_capacity, battery_capacity, load_profile, a):
    '''
    Energy from PV directly to EV load, not including energy that goes to the battery'''
    total_energy_served_by_pv = 0 
    
    load_profile = np.array(load_profile) # for usage in np.where function
    battery_max_energy_throughput = generate_data.get_battery_max_energy_throughput(battery_capacity, a) # Get max battery energy throughput
    
    battery_exists = True
    battery_energy_throughput = 0
    repurchase_battery = True

    for year in range(a['Rproj']):
        usable_pv_capacity = calculations.get_usable_pv_capacity(pv_capacity, year, a) 
        pv_output_profile = np.array(generate_data.get_pv_output(a['annual_capacity_factor'], usable_pv_capacity))
        
        # Update PV and battery capacity after degradation   
        usable_pv_capacity = calculations.get_usable_pv_capacity(pv_capacity, year, a) 
        
        if battery_exists:
            usable_battery_capacity = calculations.get_usable_battery_capacity(battery_capacity, battery_energy_throughput, battery_max_energy_throughput, year, a)
            
        # Generate PV Output profile 
        pv_output_profile = generate_data.get_pv_output(a['annual_capacity_factor'], usable_pv_capacity) 
        
        # Initialize battery repurchae cost, residual value, and cost of trickle charging (these are all zero at beginning and change throughout)
        battery_repurchase_cost = 0
            
         ###########################################################################################
          # Battery
          ###########################################################################################  
        
        # Check if the battery is still alive 
        if battery_energy_throughput < battery_max_energy_throughput: 

            pv_with_battery_output_profile, battery_throughput, cost_of_trickle_charging = generate_data.simulate_battery_storage_v4(pv_output_profile, usable_battery_capacity,  battery_energy_throughput, battery_max_energy_throughput, a)
            
            this_yr_battery_throughput = battery_throughput - battery_energy_throughput
            
            battery_energy_throughput = battery_throughput # update total battery energy throughput 
            
        else:
            if repurchase_battery: 
                battery_repurchase_cost = a['battery_cost_per_kWh'] * battery_capacity / (1 + a['discount rate'])**year # rebuy cost (discounted)
                battery_residual_value = a['battery_residual_value_factor'] * a['battery_cost_per_kWh'] * battery_capacity
                
                years_left = a['Rproj'] - year
                crf_repurchase = (a['interest rate'] * (1 + a['interest rate'])**years_left) / ((1 + a['interest rate'])**years_left - 1)

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
                
                
                
        energy_served_by_pv = np.where((pv_with_battery_output_profile > 0) & (load_profile > 0), np.minimum(load_profile, pv_with_battery_output_profile), 0)
        total_energy_served_by_pv += energy_served_by_pv.sum() - this_yr_battery_throughput
        
        

    return total_energy_served_by_pv



def get_energy_served_by_system(pv_capacity, battery_capacity, load_profile, a):
    '''
    Energy from PV directly to EV load, not including energy that goes to the battery'''
    total_energy_served_by_pv = 0 
    total_energy_served_by_batt =0
    
    load_profile = np.array(load_profile) # for usage in np.where function
    
    battery_exists = True
    this_yr_battery_throughput=0
    repurchase_battery = True
    
    year_of_battery_lifetime = 0
    total_energy_served_by_system = 0
    
    for year in range(a['Rproj']):
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

            pv_with_battery_output_profile, this_yr_battery_throughput = generate_data.simulate_battery_storage_and_get_battery_throughput(pv_output_profile, usable_battery_capacity, a)
            
            
        else:
            if repurchase_battery: 
                year_of_battery_lifetime = 0
                pv_with_battery_output_profile, this_yr_battery_throughput = generate_data.simulate_battery_storage_and_get_battery_throughput(pv_output_profile, battery_capacity, a)
                
                if a['limit_battery_repurchases']:
                    repurchase_battery = False
            else:
                pv_with_battery_output_profile = pv_output_profile 
                battery_exists = False
                usable_battery_capacity = 0
                
        energy_served_by_pv = np.where((pv_with_battery_output_profile > 0) & (load_profile > 0), np.minimum(load_profile, pv_with_battery_output_profile), 0)
        energy_served_by_system = np.where((pv_with_battery_output_profile > 0) & (load_profile > 0), np.minimum(load_profile, pv_with_battery_output_profile), 0)
        total_energy_served_by_system += energy_served_by_system.sum()
      #  total_energy_served_by_batt += this_yr_battery_throughput
       # total_energy_served_by_pv += energy_served_by_pv.sum() - this_yr_battery_throughput
        
        
    return total_energy_served_by_system

def calculate_lcoe_pv(optimal_pv_capacity, optimal_battery_capacity, load_profile, a):
    npc = get_pv_net_present_cost(optimal_pv_capacity, a)
    energy = get_energy_served_by_pv(optimal_pv_capacity, optimal_battery_capacity, load_profile, a)
    
    return npc / energy



def calculate_lcoe_batt(pv_capacity, battery_capacity, a):
   
    battery_capital_cost = a['battery_cost_per_kWh'] * battery_capacity
    loan_installment = calculate_crf(a) * (battery_capital_cost)
    battery_maintenance_cost = a['battery_annual_maintenance_cost'] * battery_capacity
    battery_energy_throughput = 0
    repurchase_battery = a['repurchase_battery']
    battery_max_energy_throughput = generate_data.get_battery_max_energy_throughput(battery_capacity, a) 
    net_cash_flows = np.zeros(a['Rproj']) 
    battery_exists = True 
    
    battery_TOTAL_energy_throughput = 0
    npc = 0

    for year in range(a['Rproj']):
        
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
            
            increase_in_throughput = battery_throughput - battery_energy_throughput
            battery_TOTAL_energy_throughput += increase_in_throughput

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
                increase_in_throughput = battery_throughput - battery_energy_throughput
                battery_TOTAL_energy_throughput += increase_in_throughput
            
            
                battery_energy_throughput = battery_throughput
                if a['limit_battery_repurchases']:
                    repurchase_battery = False
            else:
                pv_with_battery_output_profile = pv_output_profile 
                battery_maintenance_cost = 0
                battery_exists = False
                usable_battery_capacity = 0
                
        npc +=  (loan_installment + battery_maintenance_cost - battery_residual_value + cost_of_trickle_charging)/((1 + a['discount rate']) ** year)

    
    return npc/ battery_TOTAL_energy_throughput # lcoe


def compute_grid_cost(load_profile, a):
    cost = 0
    for hour, kwh in enumerate(load_profile):
        # In winter
        if hour > a['high_period_start'] and hour <= a['high_period_end']:
            off_peak = a['time_of_use_tariffs_high']['off_peak']
            standard = a['time_of_use_tariffs_high']['standard']
            peak = a['time_of_use_tariffs_high']['peak']
        else:
            off_peak = a['time_of_use_tariffs_low']['off_peak']
            standard = a['time_of_use_tariffs_low']['standard']
            peak = a['time_of_use_tariffs_low']['peak']
            
        
        if (hour % 168) > 120: # weekend
            cost += kwh * off_peak
            
        elif (hour % 24) in a['time_periods']['peak_hours']:
            cost += kwh * peak
            
        elif (hour % 24) in a['time_periods']['standard_hours']:
            cost += kwh * standard
            
        else:
            cost += kwh * off_peak
    
    return cost

def calculate_grid_tariff(pv_capacity, battery_capacity, a):
   
    total_grid_cost = 0
    # Capital Cost of Investment 
   
    
    repurchase_battery = a['repurchase_battery'] # Initialize battery repurchase bool     
    battery_exists = True # true until run out of repurchases
    
    year_of_battery_lifetime = 0

    for year in range(a['Rproj']):
        
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
        
        # Check if the battery is still alive 
        if year < a['battery_lifetime_years']:
            pv_with_battery_output_profile, cost_of_trickle_charging = generate_data.simulate_battery_storage_v5(pv_output_profile, usable_battery_capacity, a)  
        else:
            if repurchase_battery: 
                year_of_battery_lifetime = 0
                pv_with_battery_output_profile, cost_of_trickle_charging = generate_data.simulate_battery_storage_v5(pv_output_profile, battery_capacity, a)
                if a['limit_battery_repurchases']:
                    repurchase_battery = False
            else:
                pv_with_battery_output_profile = pv_output_profile 
                battery_exists = False
                usable_battery_capacity = 0
                
        net_load_profile = a['load_profile'] - pv_with_battery_output_profile
        
        total_grid_cost += compute_grid_cost(net_load_profile, a)
        
    return total_grid_cost

def get_val_kwh_ls(pv_capacity, battery_capacity, a):
    total_val_kwh_ls=0
    repurchase_battery = a['repurchase_battery']
    battery_exists = True 
    year_of_battery_lifetime = 0
    
    for year in range(a['Rproj']):
        usable_pv_capacity = calculations.get_usable_pv_capacity(pv_capacity, year, a)   
        if battery_exists:
            annual_deg = (100 * (1 - a['battery_end_of_life_perc']))  / a['battery_lifetime_years'] / 100   # annual degradation rate (%)
            usable_battery_capacity =  battery_capacity * (1 - (annual_deg * year_of_battery_lifetime))
            year_of_battery_lifetime += 1 # update year of battery lifetime
                      
        # Generate PV Output profile 
        pv_output_profile = generate_data.get_pv_output(a['annual_capacity_factor'], usable_pv_capacity)
        
        # Check if the battery is still alive 
        if year < a['battery_lifetime_years']:
            pv_with_battery_output_profile, cost_of_trickle_charging = generate_data.simulate_battery_storage_v5(pv_output_profile, usable_battery_capacity, a)

        else:
            if repurchase_battery: 
                year_of_battery_lifetime = 0
                pv_with_battery_output_profile, cost_of_trickle_charging = generate_data.simulate_battery_storage_v5(pv_output_profile, battery_capacity, a)
                if a['limit_battery_repurchases']:
                    repurchase_battery = False
            else:
                pv_with_battery_output_profile = pv_output_profile 
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
        value_of_charging_saved_by_pv_from_loadshedding = get_cost_of_missed_passengers_from_loadshedding_v2(year, saved_free_kWh, a)
        val_kwh_ls = value_of_charging_saved_by_pv_from_loadshedding.sum()
        
        total_val_kwh_ls += val_kwh_ls
    return total_val_kwh_ls

def calculate_normalized_lcoe(optimal_pv_capacity, optimal_battery_capacity, a): #lcoe_sys?
    batt_cost = get_batt_net_present_cost(optimal_pv_capacity, optimal_battery_capacity, a)
    pv_cost = get_pv_net_present_cost(optimal_pv_capacity, a)
    system_cost = batt_cost + pv_cost
    system_energy = get_energy_served_by_system(optimal_pv_capacity, optimal_battery_capacity, a['load_profile'], a)
    lcoe_system = system_cost/system_energy
    val_kwh_ls = get_val_kwh_ls(optimal_pv_capacity, optimal_battery_capacity, a)
    # numerator terms
    total_system_cost = lcoe_system * system_energy - val_kwh_ls
    total_grid_cost = calculate_grid_tariff(optimal_pv_capacity, optimal_battery_capacity, a)
    
    # denominator
    total_EV_demand = a['load_profile'].sum() * a['Rproj']
    
    normalized_lcoe = (total_system_cost + total_grid_cost) / total_EV_demand
    
    return normalized_lcoe


    
    
########## Payback period ############
def calculate_payback_period(initial_investment, cash_flows):
    # Calculate payback period
    cumulative_cash_flows = np.cumsum(cash_flows)
    payback_period = np.argmax(cumulative_cash_flows > initial_investment)
    return payback_period

########### Cost of charging ########### 

def get_cost_of_charging_v1(load_profile: np.ndarray, net_load_profile: np.ndarray,
                         time_of_use_tariffs: dict, time_periods: dict,
                         feed_in_tariff: int,
                         feed_in_tariff_bool: bool):

    # Obtain energy costs for each time period of the day
    morning_cost = time_of_use_tariffs['morning']
    afternoon_cost = time_of_use_tariffs['afternoon']
    evening_cost = time_of_use_tariffs['evening']
    night_cost = time_of_use_tariffs['night']
    
    # Obtain time periods for each time period of the day
    morning_start = time_periods['morning_start']
    afternoon_start = time_periods['afternoon_start']
    evening_start = time_periods['evening_start']
    night_start = time_periods['night_start']
    
    # Initialize total cost variables
    total_cost_no_pv = np.zeros(len(load_profile))
    total_cost_with_pv = np.zeros(len(net_load_profile))
    
    # Calculate total cost of energy with and without PV

    for i in range(len(total_cost_no_pv)):
        curr_hour_of_day = i % 24
        
    
        if morning_start <= curr_hour_of_day < afternoon_start:
            # Without PV
            total_cost_no_pv[i] = load_profile[i] * morning_cost
            # With PV
            if net_load_profile[i] < 0: # PV output is greater than EV load
                
                if feed_in_tariff_bool: # if there is a feed-in-tariff 
                    total_cost_with_pv[i] = net_load_profile[i] * feed_in_tariff # apply feed-in tariff
                else:
                    total_cost_with_pv[i] = 0 # otherwise, energy is simply curtailed and there is no cost
            else:
                total_cost_with_pv[i] = net_load_profile[i] * morning_cost
            
        elif afternoon_start <= curr_hour_of_day < evening_start:
            
            total_cost_no_pv[i] = load_profile[i] * afternoon_cost
            
            if net_load_profile[i] < 0:
                if feed_in_tariff_bool:
                    total_cost_with_pv[i] = net_load_profile[i] * feed_in_tariff
                else:
                    total_cost_with_pv[i] = 0
            else:
                total_cost_with_pv[i] = net_load_profile[i] * afternoon_cost
                
        elif evening_start <= curr_hour_of_day < night_start:
            
            total_cost_no_pv[i] = load_profile[i] * evening_cost
            
            if net_load_profile[i] < 0:
                if feed_in_tariff_bool:
                    total_cost_with_pv[i] = net_load_profile[i] * feed_in_tariff
                else:
                    total_cost_with_pv[i] = 0
            else:
                total_cost_with_pv[i] = net_load_profile[i] * evening_cost
                
        else:
            
            total_cost_no_pv[i] = load_profile[i] * night_cost
            
            if net_load_profile[i] < 0:
                if feed_in_tariff_bool:
                    total_cost_with_pv[i] = net_load_profile[i] * feed_in_tariff
                else: 
                    total_cost_with_pv[i] = 0
                
            else:
                total_cost_with_pv[i] = net_load_profile[i] * night_cost
                
        
    return total_cost_no_pv, total_cost_with_pv 







########## Cost of charging v2 (with peak,standard,off peak) #######
def get_cost_of_charging_v2(net_load_profile: np.ndarray, a):

    
    peak_hours = (a['time_periods']['peak_hours'])
    standard_hours = a['time_periods']['standard_hours']
    off_peak_hours = a['time_periods']['off_peak_hours']
    
    load_profile = a['load_profile']
    
    # Initialize total cost variables
    total_cost_no_pv = np.zeros(len(load_profile))
    total_cost_with_pv = np.zeros(len(net_load_profile))
    
    # Calculate total cost of energy with and without PV

    for i in range(len(total_cost_no_pv)):
        
        curr_hour_of_week = i % 168 
        curr_hour_of_day = i % 24
        
        if (i > a['high_period_start']) & (i <= a['high_period_end']): # high period (all peak)
            peak_cost = a['time_of_use_tariffs_high']['peak']
            standard_cost = a['time_of_use_tariffs_high']['standard']
            off_peak_cost = a['time_of_use_tariffs_high']['off_peak']
        else:
            peak_cost = a['time_of_use_tariffs_low']['peak']
            standard_cost = a['time_of_use_tariffs_low']['standard']
            off_peak_cost = a['time_of_use_tariffs_low']['off_peak']
    
        
        if curr_hour_of_week > 120: # weekend (all off-epak)
            # Without PV
            total_cost_no_pv[i] = load_profile[i] * off_peak_cost 
            # With PV
            if net_load_profile[i] < 0: # PV output is greater than EV load
                
                total_cost_with_pv[i] = 0 # otherwise, energy is simply curtailed and there is no cost
            else:
                total_cost_with_pv[i] = net_load_profile[i] * off_peak_cost
            
        elif curr_hour_of_day in peak_hours: #peak 
            
            total_cost_no_pv[i] = load_profile[i] * peak_cost 
            
            if net_load_profile[i] < 0: 
                
                total_cost_with_pv[i] = 0 
            else:
                total_cost_with_pv[i] = net_load_profile[i] * peak_cost
            
        elif curr_hour_of_day in standard_hours: #standard 
            
            total_cost_no_pv[i] = load_profile[i] * standard_cost
            
            if net_load_profile[i] < 0:
                total_cost_with_pv[i] = 0
            else:
                total_cost_with_pv[i] = net_load_profile[i] * standard_cost
                
        else: # off peak 
            
            total_cost_no_pv[i] = load_profile[i] * off_peak_cost
            
            if net_load_profile[i] < 0:
                total_cost_with_pv[i] = 0
            else:
                total_cost_with_pv[i] = net_load_profile[i] * off_peak_cost
                
        
    return total_cost_no_pv, total_cost_with_pv 


def get_energy_savings(cost_of_trickle_charging, load_profile, net_load_profile, year, a):
    
    #load_profile = a['load_profile']
    #net_load_profile = load_profile - pv_with_battery_output_profile

    peak_hours = a['time_periods']['peak_hours']
    standard_hours = a['time_periods']['standard_hours']
    off_peak_hours = a['time_periods']['off_peak_hours']
    
    # Initialize total cost variables
    total_cost_no_pv = np.zeros(len(load_profile))
    total_cost_with_pv = np.zeros(len(net_load_profile))
    
    # Calculate total cost of energy with and without PV
    for i in range(len(total_cost_no_pv)):      
        curr_hour_of_week = i % 168 
        curr_hour_of_day = i % 24
        
        if (i > a['high_period_start']) & (i <= a['high_period_end']): # high period (all peak)
            peak_cost = a['time_of_use_tariffs_high']['peak'] * (1 + a['inflation rate'])**(year - 1)
            standard_cost = a['time_of_use_tariffs_high']['standard'] * (1 + a['inflation rate'])**(year - 1)
            off_peak_cost = a['time_of_use_tariffs_high']['off_peak'] * (1 + a['inflation rate'])**(year - 1) 
        else:
            peak_cost = a['time_of_use_tariffs_low']['peak'] * (1 + a['inflation rate'])**(year - 1)
            standard_cost = a['time_of_use_tariffs_low']['standard'] * (1 + a['inflation rate'])**(year - 1)
            off_peak_cost = a['time_of_use_tariffs_low']['off_peak'] * (1 + a['inflation rate'])**(year - 1)       
             
        if curr_hour_of_week > 120: # weekend is all off-peak
            total_cost_no_pv[i] = load_profile[i] * off_peak_cost 
            if net_load_profile[i] < 0: # If PV output is greater than EV load
                total_cost_with_pv[i] = 0 # No feed-in tariff, so excess supply is curtailed 
            else:
                total_cost_with_pv[i] = net_load_profile[i] * off_peak_cost        
        elif curr_hour_of_day in peak_hours: #peak 
            total_cost_no_pv[i] = load_profile[i] * peak_cost 
            if net_load_profile[i] < 0: 
                total_cost_with_pv[i] = 0 
            else:
                total_cost_with_pv[i] = net_load_profile[i] * peak_cost         
        elif curr_hour_of_day in standard_hours: #standard 
            total_cost_no_pv[i] = load_profile[i] * standard_cost      
            if net_load_profile[i] < 0:
                total_cost_with_pv[i] = 0
            else:
                total_cost_with_pv[i] = net_load_profile[i] * standard_cost     
        else: # off peak       
            total_cost_no_pv[i] = load_profile[i] * off_peak_cost      
            if net_load_profile[i] < 0:
                total_cost_with_pv[i] = 0
            else:
                total_cost_with_pv[i] = net_load_profile[i] * off_peak_cost      
                
    return total_cost_no_pv.sum() - total_cost_with_pv.sum() - cost_of_trickle_charging



def get_energy_savings_v2(cost_of_trickle_charging, load_profile, net_load_profile, year, a):
    
    peak_hours = a['time_periods']['peak_hours']
    standard_hours = a['time_periods']['standard_hours']
    off_peak_hours = a['time_periods']['off_peak_hours']
    
    # Calculate total cost of energy with and without PV
    curr_hour_of_week = np.arange(len(load_profile)) % 168 
    curr_hour_of_day = np.arange(len(load_profile)) % 24
    
    peak_cost = np.where((curr_hour_of_week > a['high_period_start']) & (curr_hour_of_week <= a['high_period_end']),
                         a['time_of_use_tariffs_high']['peak'], a['time_of_use_tariffs_low']['peak'])
    standard_cost = np.where((curr_hour_of_week > a['high_period_start']) & (curr_hour_of_week <= a['high_period_end']),
                             a['time_of_use_tariffs_high']['standard'], a['time_of_use_tariffs_low']['standard'])
    off_peak_cost = np.where((curr_hour_of_week > a['high_period_start']) & (curr_hour_of_week <= a['high_period_end']),
                             a['time_of_use_tariffs_high']['off_peak'], a['time_of_use_tariffs_low']['off_peak'])
    
    peak_cost *= (1 + a['inflation rate'])**(year - 1)
    standard_cost *= (1 + a['inflation rate'])**(year - 1)
    off_peak_cost *= (1 + a['inflation rate'])**(year - 1)
    
    total_cost_no_pv = load_profile * ((curr_hour_of_day == off_peak_hours) * off_peak_cost
                                       + (curr_hour_of_day == peak_hours) * peak_cost
                                       + (curr_hour_of_day == standard_hours) * standard_cost)
    
    total_cost_with_pv = np.where(net_load_profile < 0, 0,
                                   net_load_profile * ((curr_hour_of_day == off_peak_hours) * off_peak_cost
                                                       + (curr_hour_of_day == peak_hours) * peak_cost
                                                       + (curr_hour_of_day == standard_hours) * standard_cost))
    
    return total_cost_no_pv.sum() - total_cost_with_pv.sum() - cost_of_trickle_charging




########### Cost of loadshedding ########### 
def get_cost_of_missed_passengers_from_loadshedding_v1(kWh_affected_by_loadshedding: list,
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
        
        curr_hour_of_week = hour % 168 
        
        curr_hour_of_day = hour % 24
        
        if morning_start <= curr_hour_of_day < afternoon_start:
            passengers_missed[hour] = kWh * morning_passenger_per_kWh

        elif afternoon_start <= curr_hour_of_day < evening_start:
            passengers_missed[hour] = kWh * afternoon_passenger_per_kWh
                
        elif evening_start <= curr_hour_of_day < night_start:
            passengers_missed[hour] = kWh * evening_passenger_per_kWh
            
        else:
            passengers_missed[hour] = kWh * night_passenger_per_kWh
            
    return passengers_missed * cost_per_passenger


def get_cost_of_missed_passengers_from_loadshedding_v2(year: int, kWh_affected_by_loadshedding: list, a: dict):



    
    
    # Obtain energy costs for each time period of the day
    peak_hours = a['time_periods']['peak_hours']
    standard_hours = a['time_periods']['standard_hours']
    off_peak_hours = a['time_periods']['off_peak_hours']


    # Initialize total cost variables
    val_kwh_missed = np.zeros(len(kWh_affected_by_loadshedding))
    
    
    for hour, kWh in enumerate(kWh_affected_by_loadshedding):
        # Find cost of doing with ICE
        kwh_L = a['kwh_km'] * (1/a['L_km'])  # kWh/L
        cost_of_ICE_operation_per_kwh = (a['cost_diesel'] / kwh_L) * (1 + a['inflation rate'])**(year - 1) # $/kWh
        
        curr_hour_of_week = hour % 168 
        curr_hour_of_day = hour % 24
        
        if (hour > a['high_period_start']) & (hour <= a['high_period_end']): # high period (all peak)
            peak_cost = a['time_of_use_tariffs_high']['peak'] * (1 + a['inflation rate'])**(year - 1)
            standard_cost = a['time_of_use_tariffs_high']['standard'] * (1 + a['inflation rate'])**(year - 1)
            off_peak_cost = a['time_of_use_tariffs_high']['off_peak'] * (1 + a['inflation rate'])**(year - 1) 
        else:
            peak_cost = a['time_of_use_tariffs_low']['peak'] * (1 + a['inflation rate'])**(year - 1)
            standard_cost = a['time_of_use_tariffs_low']['standard'] * (1 + a['inflation rate'])**(year - 1)
            off_peak_cost = a['time_of_use_tariffs_low']['off_peak'] * (1 + a['inflation rate'])**(year - 1)       
            
        if curr_hour_of_week > 120: # weekend 
            val_kwh_missed[hour] = kWh * (cost_of_ICE_operation_per_kwh - off_peak_cost)
        
        elif curr_hour_of_day in peak_hours:
            val_kwh_missed[hour] = kWh * (cost_of_ICE_operation_per_kwh - peak_cost)

        elif curr_hour_of_day in standard_hours:
            val_kwh_missed[hour] = kWh * (cost_of_ICE_operation_per_kwh - standard_cost)
                
        else:
            val_kwh_missed[hour] = kWh * (cost_of_ICE_operation_per_kwh - off_peak_cost)
                         
    return val_kwh_missed



def get_cost_of_missed_passengers_from_loadshedding_v3(year: int, kWh_affected_by_loadshedding: list, a: dict):
    # Find cost of doing with ICE
    kwh_L = a['kwh_km'] * (1/a['L_km']) # kWh/L
    cost_of_ICE_operation_per_kwh = a['cost_diesel'] / kwh_L # $/kWh
    
    # Obtain energy costs for each time period of the day
    peak_hours = a['time_periods']['peak_hours']
    standard_hours = a['time_periods']['standard_hours']
    off_peak_hours = a['time_periods']['off_peak_hours']
    
    # Initialize total cost variables
    val_kwh_missed = np.zeros(len(kWh_affected_by_loadshedding))
    
    curr_hour_of_week = np.arange(len(kWh_affected_by_loadshedding)) % 168 
    curr_hour_of_day = np.arange(len(kWh_affected_by_loadshedding)) % 24
    
    peak_cost = np.where((curr_hour_of_week > a['high_period_start']) & (curr_hour_of_week <= a['high_period_end']),
                         a['time_of_use_tariffs_high']['peak'], a['time_of_use_tariffs_low']['peak'])
    standard_cost = np.where((curr_hour_of_week > a['high_period_start']) & (curr_hour_of_week <= a['high_period_end']),
                             a['time_of_use_tariffs_high']['standard'], a['time_of_use_tariffs_low']['standard'])
    off_peak_cost = np.where((curr_hour_of_week > a['high_period_start']) & (curr_hour_of_week <= a['high_period_end']),
                             a['time_of_use_tariffs_high']['off_peak'], a['time_of_use_tariffs_low']['off_peak'])
    
    peak_cost *= (1 + a['inflation rate'])**(year - 1)
    standard_cost *= (1 + a['inflation rate'])**(year - 1)
    off_peak_cost *= (1 + a['inflation rate'])**(year - 1)
    
    val_kwh_missed = np.where(curr_hour_of_week > 120, kWh_affected_by_loadshedding * (cost_of_ICE_operation_per_kwh - off_peak_cost),
                              val_kwh_missed)
    val_kwh_missed = np.where(np.isin(curr_hour_of_day, peak_hours), kWh_affected_by_loadshedding * (cost_of_ICE_operation_per_kwh - peak_cost),
                              val_kwh_missed)
    val_kwh_missed = np.where(np.isin(curr_hour_of_day, standard_hours), kWh_affected_by_loadshedding * (cost_of_ICE_operation_per_kwh - standard_cost),
                              val_kwh_missed)
    val_kwh_missed = np.where(np.logical_not(np.logical_or(curr_hour_of_week > 120, np.isin(curr_hour_of_day, peak_hours), np.isin(curr_hour_of_day, standard_hours)) ),
                              kWh_affected_by_loadshedding * (cost_of_ICE_operation_per_kwh - off_peak_cost), val_kwh_missed)
    
    return val_kwh_missed
    
########### Carbon offsets ########### 

def get_value_of_carbon_offsets(load_profile, net_load_profile, grid_carbon_intensity, carbon_price):
    carbon_cost_gross_load = load_profile.sum() * grid_carbon_intensity *  carbon_price  # kWh * kgCO2/kWh * $/kgCO2 = $
    carbon_cost_net_load = net_load_profile.sum() * grid_carbon_intensity *  carbon_price  # kWh * kgCO2/kWh * $/kgCO2 = $ 
    return carbon_cost_gross_load - carbon_cost_net_load



def get_kwh_ls_and_op_savings(pv_capacity, battery_capacity, a):
    kwh_ls = 0
    operational_savings = 0


    # Capital Cost of Investment 
    pv_capital_cost = calculate_pv_capital_cost(pv_capacity, a)
    battery_capital_cost = a['battery_cost_per_kWh'] * battery_capacity

    ## Annual costs
    loan_installment = calculate_crf(a) * (pv_capital_cost + battery_capital_cost)
    pv_maintenance_cost = a['pv_annual_maintenance_cost'] * pv_capacity
    battery_maintenance_cost = a['battery_annual_maintenance_cost'] * battery_capacity


    battery_energy_throughput = 0 # Initialize total quantity of battery energy throughput
    repurchase_battery = a['repurchase_battery'] # Initialize battery repurchase bool 
    battery_max_energy_throughput = generate_data.get_battery_max_energy_throughput(battery_capacity, a) # Get max battery energy throughput

    net_cash_flows = np.zeros(a['Rproj']) # Initialize array to hold net cash flows 
    year_of_battery_lifetime = 0
    battery_exists = True # true until run out of repurchases
        
    for year in range(a['Rproj']):
        
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
        
        kwh_ls += sum(saved_free_kWh)
        
        
        # Profile of kWh that would be lost to load shedding WITH solar and battery
        net_load_lost_to_loadshedding = np.array([net_load_profile[i] if is_shedding and net_load_profile[i] > 0 else 0 for i, is_shedding in enumerate(loadshedding_schedule)])
        gross_load_minus_loadshedding = a['load_profile'] - gross_load_lost_to_loadshedding
        net_load_minus_loadshedding = net_load_profile - net_load_lost_to_loadshedding 
        value_of_charging_saved_by_pv_from_loadshedding = get_cost_of_missed_passengers_from_loadshedding_v2(year, saved_free_kWh, a)
        
        load_profile = gross_load_minus_loadshedding
        net_load_profile = net_load_minus_loadshedding 

                    
        energy_savings = get_energy_savings(cost_of_trickle_charging, load_profile, net_load_profile, year, a) + value_of_charging_saved_by_pv_from_loadshedding.sum()
        maintenance_costs = (pv_maintenance_cost + battery_maintenance_cost) * (1 + a['inflation rate'])**(year - 1)
        
        net_cash_flows[year] = energy_savings - loan_installment - maintenance_costs - battery_residual_value
        
        
        operational_savings += value_of_charging_saved_by_pv_from_loadshedding.sum()
        
        #print(kwh_ls, operational_savings)
        
        
        #if in final year
        if year == a['Rproj'] - 1:
            # add pv residual value to the last cash flow
            net_cash_flows[-1] += a['solar_residual_value_factor'] * a['pv_cost_per_kw'] * pv_capacity        

    npv = calculate_npv(initial_investment = 0, cash_flows = net_cash_flows, discount_rate = a['discount rate'])
    # breakpoint()

    return kwh_ls, operational_savings


def get_demand_served_by_system(pv_capacity, battery_capacity, a):

    total_energy_served_by_system = 0 


    battery_energy_throughput = 0 # Initialize total quantity of battery energy throughput
    repurchase_battery = a['repurchase_battery'] # Initialize battery repurchase bool 
    battery_max_energy_throughput = generate_data.get_battery_max_energy_throughput(battery_capacity, a) # Get max battery energy throughput

   

    battery_exists = True # true until run out of repurchases
        
    for year in range(a['Rproj']):
        
        # Update PV and battery capacity after degradation   
        usable_pv_capacity = calculations.get_usable_pv_capacity(pv_capacity, year, a) 
        
        if battery_exists:
            usable_battery_capacity = calculations.get_usable_battery_capacity(battery_capacity, battery_energy_throughput, battery_max_energy_throughput, year, a)
            
        # Generate PV Output profile 
        pv_output_profile = generate_data.get_pv_output(a['annual_capacity_factor'], usable_pv_capacity) 
        
        # Initialize battery repurchae cost, residual value, and cost of trickle charging (these are all zero at beginning and change throughout)
        battery_repurchase_cost = 0

            
            ###########################################################################################
            # Battery
            ###########################################################################################  
        
        # Check if the battery is still alive 
        if battery_energy_throughput < battery_max_energy_throughput: 

            pv_with_battery_output_profile, battery_throughput, cost_of_trickle_charging = generate_data.simulate_battery_storage_v4(pv_output_profile, usable_battery_capacity,  battery_energy_throughput, battery_max_energy_throughput, a)
            
            battery_energy_throughput = battery_throughput # update total battery energy throughput 
            
        else:
            if repurchase_battery: 
                

                usable_battery_capacity = battery_capacity # reset usable battery capacity
                battery_energy_throughput = 0 # reset battery energy used
                pv_with_battery_output_profile, battery_throughput, cost_of_trickle_charging = generate_data.simulate_battery_storage_v4(pv_output_profile, battery_capacity, battery_energy_throughput,battery_max_energy_throughput,a)
                battery_energy_throughput = battery_throughput
                if a['limit_battery_repurchases']:
                    repurchase_battery = False
            else:
                pv_with_battery_output_profile = pv_output_profile 
                battery_exists = False
                usable_battery_capacity = 0
                
                
                
                
        # loadshedding_schedule = a['load_shedding_schedule']
        # net_load_profile = a['load_profile'] - pv_with_battery_output_profile
        # gross_load_lost_to_loadshedding = np.array([a['load_profile'][i] if is_shedding else 0 for i, is_shedding in enumerate(loadshedding_schedule)]) 
        
        # # Profile of kWh that would have been lost to loadshedding but are saved by the solar + battery generation [these are beneficial, and not to be charged $$ for]
        # saved_free_kWh = [min(pv_with_battery_output_profile[i], gross_load_lost_to_loadshedding[i]) if is_shedding else 0 for i, is_shedding in enumerate(loadshedding_schedule)]
        
        # kwh_ls += sum(saved_free_kWh)
        
        
        # # Profile of kWh that would be lost to load shedding WITH solar and battery
        # net_load_lost_to_loadshedding = np.array([net_load_profile[i] if is_shedding and net_load_profile[i] > 0 else 0 for i, is_shedding in enumerate(loadshedding_schedule)])
        # gross_load_minus_loadshedding = a['load_profile'] - gross_load_lost_to_loadshedding
        # net_load_minus_loadshedding = net_load_profile - net_load_lost_to_loadshedding 
        # value_of_charging_saved_by_pv_from_loadshedding = get_cost_of_missed_passengers_from_loadshedding_v2(year, saved_free_kWh, a)
        
        # load_profile = gross_load_minus_loadshedding
        # net_load_profile = net_load_minus_loadshedding 




        
        energy_served_by_system = np.where((pv_with_battery_output_profile > 0) & (a['load_profile'] > 0), np.minimum(a['load_profile'], pv_with_battery_output_profile), 0)
      #  print(total_energy_served_by_system, energy_served_by_system.sum())
        total_energy_served_by_system += energy_served_by_system.sum()
        
            
    
    return total_energy_served_by_system




def get_cost_of_energy_pv_and_no_pv(load_profile, net_load_profile, year, a):
    
    #load_profile = a['load_profile']
    #net_load_profile = load_profile - pv_with_battery_output_profile

    peak_hours = a['time_periods']['peak_hours']
    standard_hours = a['time_periods']['standard_hours']
    off_peak_hours = a['time_periods']['off_peak_hours']
    
    # Initialize total cost variables
    total_cost_no_pv = np.zeros(len(load_profile))
    total_cost_with_pv = np.zeros(len(net_load_profile))
    
        
    # Calculate total cost of energy with and without PV
    for i in range(len(total_cost_no_pv)):      
        curr_hour_of_week = i % 168 
        curr_hour_of_day = i % 24
        
        
        if (i > a['high_period_start']) & (i <= a['high_period_end']): # high period (all peak)
            peak_cost = a['time_of_use_tariffs_high']['peak'] #* (1 + a['inflation rate'])**(year - 1)
            standard_cost = a['time_of_use_tariffs_high']['standard'] #* (1 + a['inflation rate'])**(year - 1)
            off_peak_cost = a['time_of_use_tariffs_high']['off_peak'] #* (1 + a['inflation rate'])**(year - 1) 
        else:
            peak_cost = a['time_of_use_tariffs_low']['peak'] #* (1 + a['inflation rate'])**(year - 1)
            standard_cost = a['time_of_use_tariffs_low']['standard'] #* (1 + a['inflation rate'])**(year - 1)
            off_peak_cost = a['time_of_use_tariffs_low']['off_peak'] #* (1 + a['inflation rate'])**(year - 1)       
             
        if curr_hour_of_week > 120: # weekend is all off-peak
            total_cost_no_pv[i] = load_profile[i] * off_peak_cost 
            if net_load_profile[i] < 0: # If PV output is greater than EV load
                total_cost_with_pv[i] = 0 # No feed-in tariff, so excess supply is curtailed 
            else:
                total_cost_with_pv[i] = net_load_profile[i] * off_peak_cost        
        elif curr_hour_of_day in peak_hours: #peak 
            total_cost_no_pv[i] = load_profile[i] * peak_cost 
            if net_load_profile[i] < 0: 
                total_cost_with_pv[i] = 0 
            else:
                total_cost_with_pv[i] = net_load_profile[i] * peak_cost         
        elif curr_hour_of_day in standard_hours: #standard 
            total_cost_no_pv[i] = load_profile[i] * standard_cost      
            if net_load_profile[i] < 0:
                total_cost_with_pv[i] = 0
            else:
                total_cost_with_pv[i] = net_load_profile[i] * standard_cost     
        else: # off peak       
            total_cost_no_pv[i] = load_profile[i] * off_peak_cost      
            if net_load_profile[i] < 0:
                total_cost_with_pv[i] = 0
            else:
                total_cost_with_pv[i] = net_load_profile[i] * off_peak_cost     
                
    return total_cost_no_pv.sum(), total_cost_with_pv.sum() 

def get_cost_of_energy(pv_capacity, battery_capacity, a):
    
    coe_with_pv = []
    coe_no_pv = []
    energy=[]
    # Capital Cost of Investment 
    pv_capital_cost = calculate_pv_capital_cost(pv_capacity, a)
    battery_capital_cost = a['battery_cost_per_kWh'] * battery_capacity
    
    ## Annual costs
    loan_installment = calculate_crf(a) * (pv_capital_cost + battery_capital_cost)
    pv_maintenance_cost = a['pv_annual_maintenance_cost'] * pv_capacity
    battery_maintenance_cost = a['battery_annual_maintenance_cost'] * battery_capacity
    
    
    battery_energy_throughput = 0 # Initialize total quantity of battery energy throughput
    repurchase_battery = a['repurchase_battery'] # Initialize battery repurchase bool 
    battery_max_energy_throughput = generate_data.get_battery_max_energy_throughput(battery_capacity, a) # Get max battery energy throughput
    
    net_cash_flows = np.zeros(a['Rproj']) # Initialize array to hold net cash flows 
    
    battery_exists = True # true until run out of repurchases
    year_of_battery_lifetime = 0
    #for year in tqdm(range(a['Rproj']), desc="Optimizing", ncols=100, miniters = 0, bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", disable = True):
    for year in range(a['Rproj']):
        
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
        value_of_charging_saved_by_pv_from_loadshedding = get_cost_of_missed_passengers_from_loadshedding_v2(year, saved_free_kWh, a)
        val_kwh_ls = value_of_charging_saved_by_pv_from_loadshedding.sum()
        
        if a['full_ev_fleet'] and value_of_charging_saved_by_pv_from_loadshedding.sum() > 0:
            val_kwh_ls -= a['hiring_cost'] * net_load_lost_to_loadshedding * (1/a['kwh_km']) #$/km * kwh * km/kwh = $
        
        load_profile = gross_load_minus_loadshedding
        net_load_profile = net_load_minus_loadshedding  # equals net load profile - 0 if there's no load shedding

                    
        energy_savings = get_energy_savings(cost_of_trickle_charging, load_profile, net_load_profile, year, a) + val_kwh_ls
        maintenance_costs = (pv_maintenance_cost + battery_maintenance_cost) * (1 + a['inflation rate'])**(year - 1)
        
        net_cash_flows[year] = energy_savings - loan_installment - maintenance_costs - battery_residual_value
        
    
        total_cost_no_pv, total_cost_with_pv  = get_cost_of_energy_pv_and_no_pv(load_profile, net_load_profile, year, a)
        
        coe_with_pv.append(total_cost_with_pv.sum() + cost_of_trickle_charging- val_kwh_ls)
        coe_no_pv.append(total_cost_no_pv.sum())
        energy.append(load_profile.sum())
        
        
    coe_with_system = [c/e for c,e in zip(coe_with_pv, energy)]
    coe_without_system = [c/e for c,e in zip(coe_no_pv, energy)]
    
   
    
    return np.mean(coe_with_system), np.mean(coe_without_system)