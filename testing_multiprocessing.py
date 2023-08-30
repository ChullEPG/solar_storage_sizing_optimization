import time
import multiprocessing as mp
import optimization
from constraints import cons  
import input_params as input 
import time 
import numpy as np
from scipy.optimize import minimize 
from scipy.optimize import differential_evolution
from tqdm import tqdm




# Constrain PV and Battery Capacities to be between 1 and 100 kW and kWh respectively
bounds = [(0,1000), (0,1000)]
initial_guess = [100, 100]
opt_method = 'DE' 


## store results 
pv_capacities = []
battery_capacities = []
npvs = []
times = []

start_time = time.time()

def optimize_system(solar_cost, battery_cost, load_profile, bounds, a):
    this_run_start_time = time.time()
    a['load_profile'] = load_profile
    a['pv_cost_per_kw'] = solar_cost
    a['inverter_cost_per_kw'] = solar_cost * 0.2
    a['battery_cost_per_kwh'] = battery_cost

    # Run 
    result = differential_evolution(optimization.objective_function_with_solar_and_battery_degradation_loan_v3,
                                    bounds, args=(a,), maxiter=300)

    # Extract results         
    optimal_pv_capacity = result.x[0]
    optimal_battery_capacity = result.x[1]

    # Convert to USD
    max_npv = result.fun

    this_run_end_time = time.time()
    this_run_time = (this_run_end_time - this_run_start_time) / 60

    return optimal_pv_capacity, optimal_battery_capacity, -max_npv, this_run_time

if __name__ == "__main__":
    
    annual_25_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_25_perc_ev.txt")
    annual_50_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_50_perc_ev.txt")
    annual_75_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_75_perc_ev.txt")
    annual_100_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_100_perc_ev.txt")
    
    load_profile_names = ["25% pen", "50\% pen", '75% pen', '100% pen']
    load_profile_list = [annual_25_perc_ev, annual_50_perc_ev, annual_75_perc_ev, annual_100_perc_ev]
    solar_costs = [500]#, 600, 700, 800]
    battery_costs = [200]#, 300, 400, 500]
    bounds = [(0,1000), (0,1000)]# Define your bounds here
    a = input.a # Define your 'a' here

    pool = mp.Pool(processes=mp.cpu_count())

    total_combinations = len(load_profile_list) * len(solar_costs) * len(battery_costs)
    combinations = []

    for idx, load_profile in enumerate(load_profile_list):
        for solar_cost in solar_costs:
            for battery_cost in battery_costs:
                combinations.append((solar_cost, battery_cost, load_profile, bounds, a))

    # Use starmap to parallelize the optimization process
    results = list(tqdm(pool.starmap(optimize_system, combinations), total=total_combinations, desc="Progress"))

    pool.close()
    pool.join()
    
    
    for idx, result in enumerate(results):
        solar_cost, battery_cost, load_profile, _, _ = combinations[idx]
        optimal_pv_capacity, optimal_battery_capacity, npv_value, execution_time = result

        # Print the results
        print(f"Combination {idx + 1}/{total_combinations}:")
        print("Solar Cost:", solar_cost)
        print("Battery Cost:", battery_cost)
        print("Load Profile:", load_profile)  # You might want to print the name or other information about the load profile
        print("Optimal PV Capacity:", optimal_pv_capacity, 'kW')
        print("Optimal Battery Capacity:", optimal_battery_capacity, 'kWh')
        print("NPV:", npv_value)
        print("Execution Time (minutes):", execution_time)
        print()
    
        
# if __name__ == "__main__":
#     annual_25_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_25_perc_ev.txt")
#     annual_50_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_50_perc_ev.txt")
#     annual_75_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_75_perc_ev.txt")
#     annual_100_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_100_perc_ev.txt")
    
#     load_profile_names = ["25% pen", "50\% pen", '75% pen', '100% pen']
#     load_profile_list = [annual_25_perc_ev, annual_50_perc_ev, annual_75_perc_ev, annual_100_perc_ev]
#     solar_costs = [500]#, 600, 700, 800]
#     battery_costs = [200]#, 300, 400, 500]
#     bounds = [(0,1000), (0,1000)]# Define your bounds here
#     a = input.a # Define your 'a' here

#     pool = mp.Pool(processes=mp.cpu_count())

#     results = []
#     results_with_parameters = []
    
#     total_combinations = len(load_profile_list) * len(solar_costs) * len(battery_costs)
#     processed_combinations = 0
    
#     progress_bar = tqdm(total=total_combinations, desc="Progress")
    
#     print("total combinations", total_combinations)

#     for idx, load_profile in enumerate(load_profile_list):
#         for solar_cost in solar_costs:
#             for battery_cost in battery_costs:

#                 result = pool.apply_async(optimize_system, (solar_cost, battery_cost, load_profile, bounds, a))
#                 result_with_params = (result, (load_profile_names[idx], solar_cost, battery_cost))
#                 results_with_parameters.append(result_with_params)
#                 processed_combinations += 1
#                 print(f"Processed {processed_combinations}/{total_combinations} combinations")
            
                
#                 completed_count = sum(1 for result, _ in results_with_parameters if result.ready())
#                 progress_bar.update(completed_count)  # Update the progress bar


#     pool.close()
#     pool.join()
#     progress_bar.close()
    
    
#     # Now, you can iterate through the results and their associated parameters
#     for result, (load_profile_name, solar_cost, battery_cost) in results_with_parameters:
#         # Extract and process the result
#         optimal_pv_capacity, optimal_battery_capacity, npv_value, execution_time = result.get()

#         # You can print or store the parameters along with the result
#         print("Load Profile Name:", load_profile_name)
#         print("Parameters: Solar Cost = $", solar_cost, "/kW")
#         print("Battery Cost = $", battery_cost, "/kWh")
#         print("Optimal PV Capacity:", optimal_pv_capacity, 'kW')
#         print("Optimal Battery Capacity:", optimal_battery_capacity, 'kWh')
#         print("NPV:", npv_value)
#         print("Execution Time (minutes):", execution_time)
#         print()  # Add an empty line to separate results

# if __name__ == "__main__":
#     annual_25_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_25_perc_ev.txt")
#     annual_50_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_50_perc_ev.txt")
#     annual_75_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_75_perc_ev.txt")
#     annual_100_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_100_perc_ev.txt")
#     load_profile_list = [annual_25_perc_ev, annual_50_perc_ev, annual_75_perc_ev, annual_100_perc_ev]
#     solar_costs = [500, 600, 700, 800]
#     battery_costs = [200, 300, 400, 500]
    
#     bounds = [(0,1000), (0,1000)]
#     a = input.a
#     start_time = time.time()

#     pool = mp.Pool(processes=mp.cpu_count())

#     results = pool.starmap(optimize_system, [(solar_cost, battery_cost, profile, bounds, a) for solar_cost, battery_cost, profile in zip(solar_costs, battery_costs,load_profile_list)])

#     pool.close()
#     pool.join()

#     pv_capacities, battery_capacities, npvs, times = zip(*results)

#     for i, load_profile in enumerate(zip(solar_costs,battery_costs,load_profile_list)):
#         print(f"Results for Load Profile {i + 1}, solar cost {i + 1} and battery cost {i + 1}")
#         print("Optimal PV rating: {:.2f} kW".format(pv_capacities[i]))
#         print("Optimal battery rating: {:.2f} kWh".format(battery_capacities[i]))
#         print("Maximum NPV: ${:.2f}".format(npvs[i]))
#         print("Execution time: {:.2f} minutes".format(times[i]))
        
#     end_time = time.time()
#     total_execution_time = (end_time - start_time)/60
    
#     print("Total execution time: {:.2f} minutes".format(total_execution_time))


if __name__ == "__main__":
    annual_25_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_25_perc_ev.txt")
    annual_50_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_50_perc_ev.txt")
    annual_75_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_75_perc_ev.txt")
    annual_100_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_100_perc_ev.txt")
    
    load_profile_names = ["25% pen", "50\% pen", '75% pen', '100% pen']
    load_profile_list = [annual_25_perc_ev, annual_50_perc_ev, annual_75_perc_ev, annual_100_perc_ev]
    solar_costs = [500]#, 600, 700, 800]
    battery_costs = [200]#, 300, 400, 500]
    bounds = [(0,1000), (0,1000)]# Define your bounds here
    a = input.a # Define your 'a' here

    pool = mp.Pool(processes=mp.cpu_count())

    results = []
    results_with_parameters = []
    
    total_combinations = len(load_profile_list) * len(solar_costs) * len(battery_costs)
    processed_combinations = 0
    
    progress_bar = tqdm(total=total_combinations, desc="Progress")


    for idx, load_profile in enumerate(load_profile_list):
        for solar_cost in solar_costs:
            for battery_cost in battery_costs:
                start_time = time.time()

                result = pool.apply_async(optimize_system, (solar_cost, battery_cost, load_profile, bounds, a))
                result_with_params = (result, (load_profile_names[idx], solar_cost, battery_cost))
                results_with_parameters.append(result_with_params)
                processed_combinations += 1
                print(f"Processed {processed_combinations}/{total_combinations} combinations")
            
                
                # Record the end time after executing the task
                end_time = time.time()
                
                # Calculate the execution time
                execution_time = end_time - start_time
                progress_bar.update(1)            
                print(f"Task for {load_profile_names[idx]}, Solar Cost={solar_cost}, Battery Cost={battery_cost} took {execution_time} seconds")


    pool.close()
    pool.join()
    progress_bar.close()
    
    
    # Now, you can iterate through the results and their associated parameters
    for result, (load_profile_name, solar_cost, battery_cost) in results_with_parameters:
        # Extract and process the result
        optimal_pv_capacity, optimal_battery_capacity, npv_value, execution_time = result.get()

        # You can print or store the parameters along with the result
        print("Load Profile Name:", load_profile_name)
        print("Parameters: Solar Cost = $", solar_cost, "/kW")
        print("Battery Cost = $", battery_cost, "/kWh")
        print("Optimal PV Capacity:", optimal_pv_capacity, 'kW')
        print("Optimal Battery Capacity:", optimal_battery_capacity, 'kWh')
        print("NPV:", npv_value)
        print("Execution Time (minutes):", execution_time)
        print()  # Add an empty line to separate results
