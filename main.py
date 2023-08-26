import optimization
import numpy as np
from scipy.optimize import minimize 
import input_params as input 
from scipy.optimize import differential_evolution
import time 

a = input.a 

annual_25_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_25_perc_ev.txt")
annual_50_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_50_perc_ev.txt")
annual_75_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_75_perc_ev.txt")
annual_100_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_100_perc_ev.txt")

rand_to_usd = 1/18.64


# Constrain PV and Battery Capacities to be between 1 and 100 kW and kWh respectively
bounds = [(1,1000), (1,1000)]
initial_guess = [500,500]
opt_method = 'SLSQP'


# Define the constraint functions for bounds
def constraint_x0(x):
    return x[0] - bounds[0][0]  # Lower bound for x[0]

def constraint_x1(x):
    return bounds[0][1] - x[0]  # Upper bound for x[0]

def constraint_x2(x):
    return x[1] - bounds[1][0]  # Lower bound for x[1]

def constraint_x3(x):
    return bounds[1][1] - x[1]  # Upper bound for x[1]

# Create a constraints list
constraints = (
    {'type': 'ineq', 'fun': constraint_x0},
    {'type': 'ineq', 'fun': constraint_x1},
    {'type': 'ineq', 'fun': constraint_x2},
    {'type': 'ineq', 'fun': constraint_x3}
)

# Optimize
## store results 
pv_capacities = []
battery_capacities = []
npvs = []

start_time = time.time()

if opt_method != 'DE':

    result = minimize(optimization.objective_function_with_solar_and_battery_degradation_loan_v2, x0 = initial_guess, args = (a,), bounds=bounds, constraints = constraints , method= opt_method)

else:
    
    for load_profile in [annual_25_perc_ev, annual_50_perc_ev, annual_75_perc_ev, annual_100_perc_ev]:
        a['load_profile'] = load_profile

        # Run the Differential Evolution optimization with the callback function
        result = differential_evolution(optimization.objective_function_with_solar_and_battery_degradation_loan,
                                        bounds, args=(a,),  maxiter=300)



                # Extract the optimal capacity
        optimal_pv_capacity = result.x[0]
        optimal_battery_capacity = result.x[1]

        # Calculate the minimum cash flow
        max_npv = result.fun * rand_to_usd # rescale objective back to normal and convert to USD
        
        pv_capacities.append(optimal_pv_capacity)
        battery_capacities.append(optimal_battery_capacity)
        npvs.append(max_npv)

        # Print the results
        print("Optimal PV rating: {:.2f} kW".format(optimal_pv_capacity))
        print("Optimal battery rating: {:.2f} kWh".format(optimal_battery_capacity))
        print("Maximum NPV: ${:.2f}".format(-max_npv))


# Extract the optimal capacity
optimal_pv_capacity = result.x[0]
optimal_battery_capacity = result.x[1]

# Calculate the minimum cash flow
max_npv = result.fun * rand_to_usd # rescale objective back to normal and convert to USD

# Print the results
print("Optimal PV rating: {:.2f} kW".format(optimal_pv_capacity))
print("Optimal battery rating: {:.2f} kWh".format(optimal_battery_capacity))
print("Maximum NPV: ${:.2f}".format(-max_npv))
end_time = time.time()
time_elapsed = end_time - start_time
print("Time elapsed:" , time_elapsed)


print("OPTIMAL RESULTS FOR EACH", pv_capacities, battery_capacities, npvs)