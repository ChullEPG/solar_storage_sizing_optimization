
import solar_params as solar
import battery_params as battery
import economic_params as market
#import load_ev_schedules as ev_data
import pandas as pd 
import numpy as np
import json





# Environmental inputs
grid_carbon_intensity = 0.95 # kgCO2/kWh
carbon_price = 50/1000 # $/kgCo2

# Read solar data
annual_capacity_factor = pd.read_csv("solar_profiles/renewables_ninja_profile.csv", skiprows=3)
annual_capacity_factor = annual_capacity_factor['electricity'].values

# Read EV charging schedule data
print("Loading data...")
## Varying levels of EV penetration, without load shedding
annual_25_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_25_perc_ev.txt")
annual_50_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_50_perc_ev.txt")
annual_75_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_75_perc_ev.txt")
annual_100_perc_ev = np.loadtxt(f"processed_ev_schedule_data/annual_100_perc_ev.txt")

# Mixed fleet, with load shedding
annual_ls_1 = np.loadtxt(f"processed_ev_schedule_data/annual_ls_1.txt")

# EV-only fleet, no lateness, without load shedding [for determining battery reqs to cover load shedding]
#annual_ls_1_ev_only = np.loadtxt(f"processed_ev_schedule_data/annual_ls_1_ev_only.txt")

print("Data loaded")

a = {
    # Solar PV Profile 
    'annual_capacity_factor': annual_capacity_factor,
    # EV charging load 
    'load_profile': annual_25_perc_ev,
    # PV costs 
    'pv_cost_per_kw': solar.cost_per_kw,
    'pv_annual_maintenance_cost': solar.annual_maintenance_cost,
    'solar_residual_value_factor': solar.residual_value_factor,
    # Inverter costs
    'inverter_cost_per_kw': solar.inverter_cost_per_kw, 
    'linearize_inverter_cost': True, 
    # PV specifications
    'Rproj': solar.Rproj,
    'pv_efficiency': solar.efficiency,
    'solar_annual_degradation': solar.annual_degradation,# 0.6% per year
    # Battery costs
    'battery_cost_per_kWh': battery.cost_per_kwh,
    'battery_annual_maintenance_cost': battery.annual_maintenance_cost,
    'battery_residual_value_factor': battery.residual_value_factor,
    'depth_of_discharge': battery.depth_of_discharge,
    # Battery specs
    'battery_charging_efficiency': battery.charging_efficiency,
    'battery_discharging_efficiency': battery.discharging_efficiency,
    'battery_annual_degradation': battery.annual_degradation, # 2% per year
    'battery_duration': battery.duration, 
    'battery_max_cycles': battery.max_cycles,
    'battery_max_energy_throughput': battery.energy_throughput,
    'battery_end_of_life_perc': battery.end_of_life_perc,
    'battery_trickle_charging_rate': battery.trickle_charging_rate,
    'enable_trickle_charging': True,
    'repurchase_battery': True,
    # Energy costs and schedule 
    'time_of_use_tariffs_high': market.time_of_use_tariffs_high,
    'time_of_use_tariffs_low': market.time_of_use_tariffs_low,
    'high_period_start': market.high_period_start,
    'high_period_end': market.high_period_end,
    'time_periods': market.time_periods,
    'feed_in_tariff': market.feed_in_tariff,
    # Market inputs 
    'i_no': market.i_no,
    'f': market.inflation_rate,
    'discount_rate': market.discount_rate,
    'cost_diesel': market.cost_diesel,
    # Vehicle specs
    'L_km': market.L_km, 
    'kwh_km': market.kwh_km,
    # Environmental inputs 
    'grid_carbon_intensity': grid_carbon_intensity,
    'carbon_price': carbon_price,
    # Load shedding and operational cost of serving demand during load shedding  
    # 'loadshedding_probability': loadshedding_probability,
    # 'time_passenger_per_kWh': time_passenger_per_kWh,
    # 'cost_per_passenger': cost_per_passenger,
    # Loan model
    'loan_upfront_adjustment': market.loan_upfront_adjustment,
    'loan_payback_period': market.loan_payback_period,
    'loan_interest_rate': market.loan_interest_rate,
    # Sensitivity analysis bools
    'feed_in_tariff_bool': False,
    'renewables_ninja': True,
    'carbon_price_bool': False,
    'load_shedding_bool': False,
    # # Land area 
    # 'pv_m_sq_per_kw': pv.m_sq_per_kw,
    # 'max_land_area': pv.max_land_area,
    
    # Battery cell specs
    'V_nom': battery.V_nom,
    'V_max':battery.V_max, 
    'R': battery.R, 
    'Q_nom': battery.Q_nom,
    'E_nom': battery.E_nom,
    'a_v': battery.a_v,
    'b_v': battery.b_v
}

print(battery.b_v)
