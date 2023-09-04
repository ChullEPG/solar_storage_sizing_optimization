import time
import os
import multiprocessing as mp
import optimization
import economic_analysis
from constraints import cons  
import input_params as input 
import time 
import numpy as np
from scipy.optimize import minimize 
from scipy.optimize import differential_evolution
from tqdm import tqdm




###### OPTIMIZE SYSTEM varying load profile ##########
def optimize_system(load_profile, load_profile_name, bounds, a):
    this_run_start_time = time.time()
    a['load_profile'] = load_profile

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

    return optimal_pv_capacity, optimal_battery_capacity, -max_npv, this_run_time, load_profile_name


###### OPTIMIZE SYSTEM varying load profile with COBYLA ##########
# def optimize_system_cobyla(load_profile, bounds, initial_guess, a):
#     this_run_start_time = time.time()
#     a['load_profile'] = load_profile

#     # Run 
#     result = minimize(optimization.objective_function_with_solar_and_battery_degradation_loan_v3, x0 = initial_guess, args = (a,), bounds=bounds, constraints = cons , method= 'COBYLA')
     

#     # Extract results         
#     optimal_pv_capacity = result.x[0]
#     optimal_battery_capacity = result.x[1]

#     # Convert to USD
#     max_npv = result.fun

#     this_run_end_time = time.time()
#     this_run_time = (this_run_end_time - this_run_start_time) / 60

#     return optimal_pv_capacity, optimal_battery_capacity, -max_npv, this_run_time

###### OPTIMIZE SYSTEM varying load profile and solar and storage ##########
def optimize_system_v2(solar_cost, battery_cost, load_profile, grid_load_shedding_schedule, scenario_name, bounds, a):
    this_run_start_time = time.time()
    a['load_profile'] = load_profile
    a['pv_cost_per_kw'] = solar_cost
    a['battery_cost_per_kWh'] = battery_cost
    a['load_shedding_schedule'] = grid_load_shedding_schedule
  
    if sum(grid_load_shedding_schedule) > 0:
        load_shedding_scenario = "Grid LS on"
    else:
        load_shedding_scenario = "Grid LS off"
    
    initial_guess = [500, 500]

    # Run 
    result = minimize(optimization.objective_function_with_solar_and_battery_degradation_loan_v3, x0 = initial_guess, args = (a,), bounds=bounds, constraints = cons , method= 'SLSQP')
     

    # Extract results         
    optimal_pv_capacity = result.x[0]
    optimal_battery_capacity = result.x[1]

    # Convert to USD
    max_npv = result.fun

    this_run_end_time = time.time()
    this_run_time = (this_run_end_time - this_run_start_time) / 60

    return optimal_pv_capacity, optimal_battery_capacity, -max_npv, this_run_time, scenario_name, load_shedding_scenario



###############  STARMAP #2  #################### 
if __name__ == "__main__":
    
    start_time = time.time()
    
    
    print("ALL LOAD PROFILES WITH SOLAR AND BATT SENSITIVITY")
    
    annual_25_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_25_perc_ev.txt")
    annual_50_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_50_perc_ev.txt")
    annual_75_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_75_perc_ev.txt")
    annual_100_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_100_perc_ev.txt")
    
    annual_25_perc_ls_1 = np.loadtxt(f"processed_ev_schedule_data/25_perc/annual_ls_1.txt") 
    annual_50_perc_ls_1 = np.loadtxt(f"processed_ev_schedule_data/50_perc/annual_ls_1.txt") 
    annual_75_perc_ls_1 = np.loadtxt(f"processed_ev_schedule_data/75_perc/annual_ls_1.txt") 
    annual_100_perc_ls_1 = np.loadtxt(f"processed_ev_schedule_data/100_perc/annual_ls_1.txt") 
    
    annual_25_perc_ls_2 = np.loadtxt(f"processed_ev_schedule_data/25_perc/annual_ls_2.txt") 
    annual_50_perc_ls_2 = np.loadtxt(f"processed_ev_schedule_data/50_perc/annual_ls_2.txt") 
    annual_75_perc_ls_2 = np.loadtxt(f"processed_ev_schedule_data/75_perc/annual_ls_2.txt") 
    annual_100_perc_ls_2 = np.loadtxt(f"processed_ev_schedule_data/100_perc/annual_ls_2.txt") 
    
    annual_25_perc_ls_3 = np.loadtxt(f"processed_ev_schedule_data/25_perc/annual_ls_3.txt") 
    annual_50_perc_ls_3 = np.loadtxt(f"processed_ev_schedule_data/50_perc/annual_ls_3.txt") 
    annual_75_perc_ls_3 = np.loadtxt(f"processed_ev_schedule_data/75_perc/annual_ls_3.txt") 
    annual_100_perc_ls_3 = np.loadtxt(f"processed_ev_schedule_data/100_perc/annual_ls_3.txt") 
    
    

    
    scenario_names = ["25% No LS", "50% No LS", '75% No LS', '100% No LS', 
                     "25% LS1", '50% LS1', '75% LS1', '100% LS1']      
    load_profile_list = [annual_25_perc_ev, annual_50_perc_ev, annual_75_perc_ev, annual_100_perc_ev]
    load_profile_list_ls_1 = [annual_25_perc_ls_1,annual_50_perc_ls_1, annual_75_perc_ls_1, annual_100_perc_ls_1]
    load_profile_list = load_profile_list + load_profile_list_ls_1 
    grid_load_shedding_schedules = [input.ls_annual_empty, input.ls_annual_1]
                         
    # load_profile_list = [annual_25_perc_ev, annual_50_perc_ev, annual_75_perc_ev, annual_100_perc_ev]
    # #load_profile_list_ls_1 = [annual_25_perc_ls_1,annual_50_perc_ls_1, annual_75_perc_ls_1, annual_100_perc_ls_1]
    # load_profile_list_ls_2 = [annual_25_perc_ls_2, annual_50_perc_ls_2, annual_75_perc_ls_2, annual_100_perc_ls_2]
    # load_profile_list_ls_3 = [annual_25_perc_ls_3, annual_50_perc_ls_3, annual_75_perc_ls_3, annual_100_perc_ls_3]
    
    
    #load_profile_list = load_profile_list #+ load_profile_list_ls_2 + load_profile_list_ls_3 
   # grid_load_shedding_schedules = [input.ls_annual_2]
    #next - grid LS ON, Ev scheduling LS OFF (scp before doing next )
    #grid_load_shedding_schedules = [input.ls_annual_3]
    # then - grid LS OFF, Ev scheduling LS ON 
    # scenario_names = ["25% LS2", '50% LS2', '75% LS2', '100% LS2',
    #                   "25% LS3", '50% LS3', '75% LS3', '100% LS3']         
    # load_profile_list = load_profile_list_ls_2 + load_profile_list_ls_3
    # grid_load_shedding_schedules = [input.ls_annual_empty]
    # next, back to this one in case it messed up
    # grid_load_shedding_schedules = [input.ls_annual_3]
    # scenario_names = ["25% No LS", "50% No LS", "75% No LS", "100% No LS"]
    # load_profile_list = [annual_25_perc_ev, annual_50_perc_ev, annual_75_perc_ev, annual_100_perc_ev]




    # solar_costs = [500, 600, 700, 800, 900] 
    # battery_costs = [100, 200, 300, 400, 500]
    solar_costs = [500]
    battery_costs = [300]
   
    
    bounds = [(0,1000), (0,1000)]
    a = input.a 
    pool = mp.Pool(processes=mp.cpu_count())

    total_combinations = len(load_profile_list) * len(solar_costs) * len(battery_costs) #len(grid_load_shedding_schedules)
    combinations = []

    for idx, load_profile in enumerate(load_profile_list):
        for jdx, grid_load_shedding_schedule in enumerate(grid_load_shedding_schedules): 
            for solar_cost in solar_costs:
                for battery_cost in battery_costs:
                    combinations.append((solar_cost, battery_cost, load_profile, grid_load_shedding_schedule, scenario_names[idx], bounds, a))

    # Use starmap to parallelize the optimization process
    results = list(tqdm(pool.starmap(optimize_system_v2, combinations), total=total_combinations, desc="Progress"))

    pool.close()
    pool.join()
    
        
    for idx, result in enumerate(results):
        solar_cost, battery_cost, load_profile, grid_load_shedding_schedule, scenario_name, _, _, = combinations[idx]
        optimal_pv_capacity, optimal_battery_capacity, npv_value, execution_time, scenario_name, grid_load_shedding_scenario = result
        
        
        #Make directory scenario_name if doesn't exist
        if not os.path.exists(f"../results/{grid_load_shedding_scenario}/{scenario_name}"):   
            os.makedirs(f"../results/{grid_load_shedding_scenario}/{scenario_name}")
            
        # Create the file name
        file_name = f"../results/{grid_load_shedding_scenario}/{scenario_name}/solar={solar_cost}_battery={battery_cost}.txt"
        
        # Write the results to the file
        with open(file_name, "w") as f2:
            f2.write(f"Optimal PV Capacity: {optimal_pv_capacity} kW\n")
            f2.write(f"Optimal Battery Capacity: {optimal_battery_capacity} kWh\n")
            f2.write(f"NPV: {npv_value}\n")
            # Calculate investment cost, ROI, and LCOE
            investment_cost = economic_analysis.calculate_pv_capital_cost(optimal_pv_capacity, a) + (a['battery_cost_per_kWh'] * optimal_battery_capacity)
            f2.write(f"Investment cost: ${investment_cost}\n") 
            roi = npv_value / investment_cost
            f2.write(f"ROI: {roi} %\n")
            lcoe_pv = economic_analysis.calculate_lcoe_pv(optimal_pv_capacity, load_profile, a)
            lcoe_batt = economic_analysis.calculate_lcoe_batt(optimal_pv_capacity, optimal_battery_capacity, a)
            f2.write(f"LCOE_PV: {lcoe_pv}$/kWh \n")
            f2.write(f"LCOE_Batt: {lcoe_batt}$/kWh \n")
            p_grid = economic_analysis.compute_p_grid(load_profile, a)
            f2.write(f"P_grid: {p_grid}$/kWh \n")
            lps = load_profile.sum()
            f2.write(f"Load profile sum {lps} \n")
        
        # Print the results
        print(f"Combination {idx + 1}/{total_combinations}:")
        print("Solar Cost:", solar_cost)
        print("Battery Cost:", battery_cost)
        print("Scenario:", scenario_name)  # You might want to print the name or other information about the load profile
        print("Optimal PV Capacity:", optimal_pv_capacity, 'kW')
        print("Optimal Battery Capacity:", optimal_battery_capacity, 'kWh')
        print("NPV:", npv_value)
        print("Investment cost: $", investment_cost) 
        print("LCOE PV", lcoe_pv)
        print("LCOE Batt", lcoe_batt)
        print("Avg grid price", p_grid)
        print("Execution Time (minutes):", execution_time)
        print()

            
    end_time = time.time()
    
    total_execution_time = (end_time - start_time)/60
    
    print("Total program execution time:", total_execution_time)
    # print number of true observations in a['load_shedding_schdule'] array
    

    

####### OPTIMIZE SYSTEM WITH COBYLA / SLSQP AND VARYING INITIAL GUESSES ######

# if __name__ == "__main__":
    
#     annual_25_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_25_perc_ev.txt")
#     annual_50_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_50_perc_ev.txt")
#     annual_75_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_75_perc_ev.txt")
#     annual_100_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_100_perc_ev.txt")
    
#     profile = annual_100_perc_ev
    
#     load_profile_list = [annual_25_perc_ev, annual_50_perc_ev, annual_75_perc_ev, annual_100_perc_ev]

#     bounds = [(0,1000), (0,1000)]
#     #initial_guesses = [[50 + 50 * i, 50 + 50 * i] for i in range(20)]
#     #initial_guesses = [[0 + 200 * i, 0 + 200 * i] for i in range(5)]
#     initial_guesses = [[0,0]]
#     print(initial_guesses)
#     #intial_guess = [500,500]
#     a = input.a
#     start_time = time.time()

#     pool = mp.Pool(processes=mp.cpu_count())

#     results = pool.starmap(optimize_system_cobyla, [(profile, bounds, initial_guess ,a) for initial_guess in initial_guesses])

#     pool.close()
#     pool.join()

#     pv_capacities, battery_capacities, npvs, times = zip(*results)

#     for i, ig in enumerate(initial_guesses):
#         print(f"Results for Initial Guess:", ig)
#         print("Optimal PV rating: {:.2f} kW".format(list(pv_capacities)[i]))
#         print("Optimal battery rating: {:.2f} kWh".format(list(battery_capacities)[i]))
#         print("Maximum NPV: ${:.2f}".format(list(npvs)[i]))
#         print("Execution time: {:.2f} minutes".format(list(times)[i]))
#         # write the results to a file
        
        
#     end_time = time.time()
#     total_execution_time = (end_time - start_time)/60
    
#     print("Total execution time: {:.2f} minutes".format(total_execution_time))

                
                

###### OPTIMIZE SYSTEM varying load profile, solar and battery costs ##########
# def optimize_system(solar_cost, battery_cost, load_profile, bounds, a):
#     this_run_start_time = time.time()
#     a['load_profile'] = load_profile
#     a['pv_cost_per_kw'] = solar_cost
#     a['inverter_cost_per_kw'] = solar_cost * 0.2
#     a['battery_cost_per_kwh'] = battery_cost

#     # Run 
#     result = differential_evolution(optimization.objective_function_with_solar_and_battery_degradation_loan_v3,
#                                     bounds, args=(a,), maxiter=300)

#     # Extract results         
#     optimal_pv_capacity = result.x[0]
#     optimal_battery_capacity = result.x[1]

#     # Convert to USD
#     max_npv = result.fun

#     this_run_end_time = time.time()
#     this_run_time = (this_run_end_time - this_run_start_time) / 60

#     return optimal_pv_capacity, optimal_battery_capacity, -max_npv, this_run_time


###############  STARMAP #2  #################### 
# if __name__ == "__main__":
    
#     start_time = time.time()
    
#     annual_25_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_25_perc_ev.txt")
#     annual_50_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_50_perc_ev.txt")
#     annual_75_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_75_perc_ev.txt")
#     annual_100_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_100_perc_ev.txt")
    
#     load_profile_names = ["25% pen", "50\% pen", '75% pen', '100% pen']
#     load_profile_list = [annual_25_perc_ev, annual_50_perc_ev, annual_75_perc_ev, annual_100_perc_ev]
#     solar_costs = [700]
#     battery_costs = [400]
#     bounds = [(0,1000), (0,1000)]# Define your bounds here
#     a = input.a # Define your 'a' here

#     pool = mp.Pool(processes=mp.cpu_count())

#     total_combinations = len(load_profile_list) * len(solar_costs) * len(battery_costs)
#     combinations = []

#     for idx, load_profile in enumerate(load_profile_list):
#         for solar_cost in solar_costs:
#             for battery_cost in battery_costs:
#                 combinations.append((solar_cost, battery_cost, load_profile, bounds, a))

#     # Use starmap to parallelize the optimization process
#     results = list(tqdm(pool.starmap(optimize_system, combinations), total=total_combinations, desc="Progress"))

#     pool.close()
#     pool.join()
    
    
#     for idx, result in enumerate(results):
#         solar_cost, battery_cost, load_profile, _, _ = combinations[idx]
#         optimal_pv_capacity, optimal_battery_capacity, npv_value, execution_time = result

#         # Print the results
#         print(f"Combination {idx + 1}/{total_combinations}:")
#         print("Solar Cost:", solar_cost)
#         print("Battery Cost:", battery_cost)
#         print("Load Profile:", load_profile.sum())  # You might want to print the name or other information about the load profile
#         print("Optimal PV Capacity:", optimal_pv_capacity, 'kW')
#         print("Optimal Battery Capacity:", optimal_battery_capacity, 'kWh')
#         print("NPV:", npv_value)
#         print("Execution Time (minutes):", execution_time)
#         print()
        
#     end_time =time.time()
    
#     total_execution_time = (end_time - start_time)/60
    
#     print("Total program execution time:", total_execution_time)
    
    ###############  ASYNC  #################### 
        
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


###############  STARMAP #1  #################### 


# if __name__ == "__main__":
    
#     annual_25_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_25_perc_ev.txt")
#     annual_50_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_50_perc_ev.txt")
#     annual_75_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_75_perc_ev.txt")
#     annual_100_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_100_perc_ev.txt")
    
#     load_profile_list = [annual_25_perc_ev, annual_50_perc_ev, annual_75_perc_ev, annual_100_perc_ev]

#     bounds = [(0,1000), (0,1000)]
#     a = input.a
#     start_time = time.time()

#     pool = mp.Pool(processes=mp.cpu_count())

#     results = pool.starmap(optimize_system, [(profile, bounds, a) for profile in load_profile_list])

#     pool.close()
#     pool.join()

#     pv_capacities, battery_capacities, npvs, times = zip(*results)

#     for i, load_profile in enumerate(load_profile_list):
#         print(f"Results for Load Profile {i + 1}")
#         print("Optimal PV rating: {:.2f} kW".format(pv_capacities[i]))
#         print("Optimal battery rating: {:.2f} kWh".format(battery_capacities[i]))
#         print("Maximum NPV: ${:.2f}".format(npvs[i]))
#         print("Execution time: {:.2f} minutes".format(times[i]))
        
#     end_time = time.time()
#     total_execution_time = (end_time - start_time)/60
    
#     print("Total execution time: {:.2f} minutes".format(total_execution_time))


###############  ASYNC  #################### 

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


#     for idx, load_profile in enumerate(load_profile_list):
#         for solar_cost in solar_costs:
#             for battery_cost in battery_costs:
#                 start_time = time.time()

#                 result = pool.apply_async(optimize_system, (solar_cost, battery_cost, load_profile, bounds, a))
#                 result_with_params = (result, (load_profile_names[idx], solar_cost, battery_cost))
#                 results_with_parameters.append(result_with_params)
#                 processed_combinations += 1
#                 print(f"Processed {processed_combinations}/{total_combinations} combinations")
            
                
#                 # Record the end time after executing the task
#                 end_time = time.time()
                
#                 # Calculate the execution time
#                 execution_time = end_time - start_time
#                 progress_bar.update(1)            
#                 print(f"Task for {load_profile_names[idx]}, Solar Cost={solar_cost}, Battery Cost={battery_cost} took {execution_time} seconds")


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





    
    
    