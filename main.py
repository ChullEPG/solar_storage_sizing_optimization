import optimization
from constraints import cons  
import input_params as input 
import time 
import numpy as np
from scipy.optimize import minimize 
from scipy.optimize import differential_evolution


a = input.a 

annual_25_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_25_perc_ev.txt")
annual_50_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_50_perc_ev.txt")
annual_75_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_75_perc_ev.txt")
annual_100_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_100_perc_ev.txt")

# Constrain PV and Battery Capacities to be between 1 and 100 kW and kWh respectively
bounds = [(0,1000), (0,1000)]
initial_guess = [200, 100]
opt_method = 'SLSQP' 


## store results 
pv_capacities = []
battery_capacities = []
npvs = []
times = []

start_time = time.time()

if opt_method != 'DE':

    result = minimize(optimization.objective_function_with_changed_load_shedding, x0 = initial_guess, args = (a,), bounds=bounds, constraints = cons , method= opt_method)

else:
    #load_profile_list = [annual_25_perc_ev, annual_50_perc_ev, annual_75_perc_ev, annual_100_perc_ev]
    #load_profile_list = [annual_50_perc_ev, annual_75_perc_ev, annual_100_perc_ev]
    
    #for load_profile in load_profile_list:
       # this_run_start_time = time.time()
       # a['load_profile'] = load_profile
      
        # Run 
    result = differential_evolution(optimization.objective_function_with_solar_and_battery_degradation_loan_v3,
                                        bounds, args=(a,),  maxiter=300)



        # # Extract results         
        # optimal_pv_capacity = result.x[0]
        # optimal_battery_capacity = result.x[1]

        # # Convert to USD
        # max_npv = result.fun # 
        
        # this_run_end_time = time.time()
        # this_run_time = (this_run_end_time - this_run_start_time)/60
        
        # pv_capacities.append(optimal_pv_capacity)
        # battery_capacities.append(optimal_battery_capacity)
        # npvs.append(-max_npv)
        # times.append(this_run_time)

        # # Print the results
        # print("Optimal PV rating: {:.2f} kW".format(optimal_pv_capacity))
        # print("Optimal battery rating: {:.2f} kWh".format(optimal_battery_capacity))
        # print("Maximum NPV: ${:.2f}".format(-max_npv))


# Extract the optimal capacity
optimal_pv_capacity = result.x[0]
optimal_battery_capacity = result.x[1]

# Calculate the minimum cash flow
max_npv = result.fun  # rescale objective back to normal and convert to USD

# Print the results
print("Optimal PV rating: {:.2f} kW".format(optimal_pv_capacity))
print("Optimal battery rating: {:.2f} kWh".format(optimal_battery_capacity))
print("Maximum NPV: ${:.2f}".format(-max_npv))
print("Time for each run:", times)

end_time = time.time()
time_elapsed = (end_time - start_time)/60
print("Total time elapsed:" , round(time_elapsed), "minutes")


print("OPTIMAL RESULTS FOR EACH", pv_capacities, battery_capacities, npvs)