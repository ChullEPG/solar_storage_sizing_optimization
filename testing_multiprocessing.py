import optimization
import numpy as np
import input_params as input
from scipy.optimize import differential_evolution
from multiprocessing import Pool
import time 

# Define a function to perform optimization
def optimize_once(seed, bounds, a):
    # Set a different random seed for each optimization run
    np.random.seed(seed)

    # Perform a single optimization run
    result = differential_evolution(
        optimization.objective_function_with_solar_and_battery_degradation_loan,
        bounds, args=(a,), maxiter=300
    )
    
    return result

if __name__ == "__main__":
    # Number of parallel optimization runs
    num_processes = 4  # Adjust as needed

    # Bounds and input parameters
    bounds = [(1, 1000), (1, 1000)]
    a = input.a
    
    start_time = time.time()

    # Create a Pool of processes
    with Pool(num_processes) as pool:
        # Generate a list of random seeds for parallel optimization runs
        random_seeds = np.random.randint(0, 1000, num_processes)

        # Perform parallel optimization runs
        results = pool.starmap(optimize_once, [(seed, bounds, a) for seed in random_seeds])
        
    end_time = time.time()
    
    execution_time = end_time - start_time

    # Find the best result among all runs
    best_result = min(results, key=lambda x: x.fun)

    # Print the best result
    print("Best Result:")
    print(best_result)
    print(f"Total Execution Time: {execution_time:.2f} seconds")

    # You can access other information from best_result as needed
    # For example, best_result.x gives the optimal parameters
