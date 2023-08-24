import optimization
import time
from scipy.optimize import minimize 
import input_params as input 

a = input.a 

#Track time

()


# Constrain PV and Battery Capacities to be between 1 and 100 kW and kWh respectively
bounds = [(1,1000), (1,1000)]
initial_guess = [900, 100]

# Optimize
start_time = time.time
result = minimize(optimization.objective_function_with_solar_and_battery_degradation_loan, x0 = initial_guess, args = (a,), bounds=bounds, method='SLSQP')
#time_taken = time.time() - start_time

# Extract the optimal capacity
optimal_pv_capacity = result.x[0]
optimal_battery_capacity = result.x[1]

# Calculate the minimum cash flow
max_npv = result.fun

# Print the results
print("Optimal PV rating: {:.2f} kW".format(optimal_pv_capacity))
print("Optimal battery rating: {:.2f} kWh".format(optimal_battery_capacity))
print("Maximum NPV: ${:.2f}".format(-max_npv))
# print time taken
