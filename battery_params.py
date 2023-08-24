

# Battery cost
size = 2400 #Wh
cost_per_battery = 12308.12 # Rand
cost_per_wh = cost_per_battery/size

# convert to kWh
cost_per_kwh = cost_per_wh * 1e3   # R/kWh 

annual_maintenance_cost = 200 # R/kW

# Battery system specifications
charging_efficiency = 0.99 #%
discharging_efficiency = 0.99 #% 
annual_degradation = 0.005 # % per year
duration = 2 # hours (for max power draw
depth_of_discharge = 0.90 # %

# lifetime ratings
energy_throughput = 2e5 #kWh - total energy battery can output in lifetime
max_cycles = 6000 # num cycles battery can run through in lifetime
end_of_life_perc = 0.80 # percent of original capacity left at end of life 

# Residual value
residual_value_factor = 0.10 # % of initial cost

# Trickle charge
trickle_charging_rate = 2.2 # kWh
enable_trickle_charging = True


# Battery cell specs
V_nom = 3.7
V_max = 4.15
R = 148 # mOhm
Q_nom = 2.2 # Ah
E_nom = Q_nom * V_nom # Wh
a_v = 67.92
b_v = 3.592