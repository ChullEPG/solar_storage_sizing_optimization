import numpy as np
import pyomo


def optimize_battery_to_cover_loadshedding(load_profile, pv_output_profile, loadshedding_schedule,
                                           battery_capacity, battery_duration,
                                           charging_efficiency, discharging_efficiency):
    
    
    net_load_profile = load_profile - pv_output_profile # Calculate the net load
    
    battery_power_rating = battery_capacity / battery_duration # Calculate the power rating of the battery
    battery_state = 0 # Initialize the battery state
    battery_states = np.zeros(len(pv_output_profile)) # Initialize an array to keep track of the battery state

    for hour, net_load in enumerate(net_load_profile):
        
        battery_room = battery_capacity - battery_state # Calculate the amount of room left in the battery
        
        if net_load > 0: 
            if loadshedding_schedule[hour]: # If there is loadshedding, discharge the battery
                battery_states[hour] = battery_states[hour - 1] - net_load * discharging_efficiency
                
        if net_load < 0: 
            # The PV system is producing more energy than the load requires
            # Charge the battery with the excess energy
            energy_drawn_from_pv = min(battery_room/charging_efficiency, -net_load, battery_power_rating)
            energy_stored_in_battery = energy_drawn_from_pv * charging_efficiency
            
            # Update battery state 
            battery_state = battery_state + energy_stored_in_battery
            
            # Losses 
            loss_from_efficiency = energy_drawn_from_pv - energy_stored_in_battery
            loss_from_curtailment = -net_load - energy_drawn_from_pv      
                
                
    
    
    
    return battery_states





    
from pyomo.environ import ConcreteModel, Var, NonNegativeReals, Objective, maximize, Constraint, RangeSet, Param
from pyomo.opt import SolverFactory
import numpy as np

def optimize_battery_energy_flow(load_profile, pv_output_profile, discharge_values):
    num_hours = len(load_profile)

    # Create a Pyomo model
    model = ConcreteModel()

    # Set indices for the hours of the year
    model.HOURS = RangeSet(num_hours)

    # Decision variable: battery discharge amount in each hour
    model.discharge = Var(model.HOURS, within=NonNegativeReals)

    # Objective function: maximize the total value of battery discharges
    model.total_value = Objective(expr=sum(discharge_values[i] * model.discharge[i] for i in model.HOURS), sense=maximize)

    # Constraints: battery energy balance
    model.energy_balance = Constraint(model.HOURS, rule=lambda model, i: model.discharge[i] <= pv_output_profile[i] - load_profile[i])

    # Solve the optimization problem
    solver = SolverFactory('glpk')  # Change the solver based on your preference and availability
    solver.solve(model)

    # Extract the optimized battery discharge values
    optimized_discharge = np.array([model.discharge[i].value for i in model.HOURS])

    # Return the optimized battery discharge values
    return optimized_discharge
