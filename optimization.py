# Description: This file contains the objective functions for the optimization problem.
import economic_analysis
import generate_data
import calculations
from tqdm import tqdm

# With loan
def objective_function_with_solar_and_battery_degradation_loan(x, a):
    
    pv_capacity =x[0]
    battery_capacity= x[1]  # Bound x[1] between 1 and 1000
    # if opt_method == 'SQSLP':
    #     # Decision variables - PV capacity and Battery capacity 
    #     pv_capacity = x[0]
    #     battery_capacity = x[1]
    # elif opt_method == 'COBYLA':
        
    
        
    
    # Capital Cost of Investment 
    total_capital_cost = economic_analysis.calculate_capital_cost(pv_capacity, battery_capacity, a, linearize_inverter_cost = a['linearize_inverter_cost'])
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
    
    return -npv # scale objective to roughly order 1 to improve the gradient-based optimization process
