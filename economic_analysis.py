import numpy as np


########### NPV ########### 

def calculate_npv(initial_investment, cash_flows, discount_rate):
    
    values = []
    for idx, cash_flow in enumerate(cash_flows):
        this_year_value = cash_flow /(1 + discount_rate)**idx
        values.append(this_year_value)
            
    total_benefits = sum(values)
    total_costs = initial_investment
    npv = total_benefits - total_costs 
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

def calculate_pv_capital_cost(pv_capacity, a, linearize_inverter_cost = False):
    
    # find the inverter cost using a['inverter_cost_schedule'] and the pv_capacity 
    # to do so, must find the closest pv capacity in the schedule
    
    if linearize_inverter_cost:
        inverter_cost = pv_capacity * a['inverter_cost_per_kw'] 
        
    else:  # Use cost schedule
        pv_capacities = a['inverter_cost_schedule'].keys()
        closest_pv_capacity = min(pv_capacities, key=lambda x:abs(x-pv_capacity))
        inverter_cost = a['inverter_cost_schedule'][closest_pv_capacity]
        
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
    r = a['interest rate']
    crf = (r * (1 + r)**a['Rproj']) / ((1 + r)**a['Rproj'] - 1)
    return crf


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

    
    peak_hours = a['time_periods']['peak_hours']
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




def get_energy_savings(cost_of_trickle_charging, pv_with_battery_output_profile, year, a):
    
    load_profile = a['load_profile']
    net_load_profile = load_profile - pv_with_battery_output_profile

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


def get_cost_of_missed_passengers_from_loadshedding_v2(kWh_affected_by_loadshedding: list, a: dict):


    time_of_use_tariffs = a['time_of_use_tariffs']
    time_periods = a['time_periods']
    L_km = a['L_km']
    kwh_km = a['kwh_km']
    cost_diesel = a['cost_diesel']
    
    # Obtain energy costs for each time period of the day
    peak_cost = time_of_use_tariffs['peak']
    standard_cost = time_of_use_tariffs['standard']
    off_peak_cost = time_of_use_tariffs['off_peak']
    
    peak_hours = time_periods['peak_hours']
    standard_hours = time_periods['standard_hours']
    off_peak_hours = time_periods['off_peak_hours']
    
    

    # Initialize total cost variables
    val_kwh_missed = np.zeros(len(kWh_affected_by_loadshedding))
    
    # Find cost of doing with ICE
    kwh_L = kwh_km * (1/L_km) # kWh/L
    cost_of_ICE_operation_per_kwh = cost_diesel / kwh_L # $/kWh
    
    

    
    for hour, kWh in enumerate(kWh_affected_by_loadshedding):
        
        curr_hour_of_week = hour % 168 
        
        curr_hour_of_day = hour % 24
            
        if curr_hour_of_week > 120: # weekend 
            val_kwh_missed[hour] = kWh * (cost_of_ICE_operation_per_kwh - off_peak_cost)
        
        elif curr_hour_of_day in peak_hours:
            val_kwh_missed[hour] = kWh * (cost_of_ICE_operation_per_kwh - peak_cost)

        elif curr_hour_of_day in standard_hours:
            val_kwh_missed[hour] = kWh * (cost_of_ICE_operation_per_kwh - standard_cost)
                
        else:
            val_kwh_missed[hour] = kWh * (cost_of_ICE_operation_per_kwh - off_peak_cost)
                    
    return val_kwh_missed
    
########### Carbon offsets ########### 

def get_value_of_carbon_offsets(load_profile, net_load_profile, grid_carbon_intensity, carbon_price):
    carbon_cost_gross_load = load_profile.sum() * grid_carbon_intensity *  carbon_price  # kWh * kgCO2/kWh * $/kgCO2 = $
    carbon_cost_net_load = net_load_profile.sum() * grid_carbon_intensity *  carbon_price  # kWh * kgCO2/kWh * $/kgCO2 = $ 
    return carbon_cost_gross_load - carbon_cost_net_load