
import solar_params as solar
import battery_params as battery
import economic_params as market
import load_shedding_schedules 
from generate_data import generate_loadshedding_profile
#import load_ev_schedules as ev_data
import pandas as pd 
import numpy as np
# import json
import pdb


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


## Load shedding schedule 
ls_1 = generate_loadshedding_profile(load_shedding_schedules.ls_1)
ls_2 = generate_loadshedding_profile(load_shedding_schedules.ls_2)
ls_3 = generate_loadshedding_profile(load_shedding_schedules.ls_3)
ls_4 = generate_loadshedding_profile(load_shedding_schedules.ls_4)

## Append them together to make weekly thingy
ls_order_1 = np.concatenate((ls_1, ls_2, ls_3, ls_4, ls_1, ls_2, ls_3), axis = 0)
ls_order_2 = np.concatenate((ls_3, ls_3, ls_2, ls_2, ls_2, ls_2, ls_1), axis = 0)
ls_order_3 = np.concatenate((ls_2, ls_1, ls_1, ls_1, ls_1, ls_4, ls_4), axis = 0)
# Make annual by repeating it 52 times and adding one to the end (MAKE SURE SAME AS IN LOAD_EV_SCHEDULES)
ls_annual_1 = np.concatenate([np.tile(ls_order_1, 52), ls_1], axis = 0)
ls_annual_2 = np.concatenate([np.tile(ls_order_2, 52), ls_2], axis = 0)
ls_annual_3 = np.concatenate([np.tile(ls_order_2, 52), ls_4], axis = 0)
# Empty ls_annual schedule
ls_annual_empty = np.zeros(8760)
     

print("Data loaded")

a = {
    # Solar PV Profile 
    'annual_capacity_factor': annual_capacity_factor,
    # EV charging load 
    'load_profile': annual_25_perc_ev,
    'load_profile_2': annual_50_perc_ev,
    'load_profile_3': annual_75_perc_ev,
    'load_profile_4': annual_100_perc_ev,
    # PV costs 
    'pv_cost_per_kw': solar.cost_per_kw,
    'pv_annual_maintenance_cost': solar.annual_maintenance_cost,
    'solar_residual_value_factor': solar.residual_value_factor,
    # PV specifications
    'Rproj': solar.Rproj,
    'solar_annual_degradation': solar.annual_degradation,# 0.6% per year
    # Inverter costs
    'inverter_cost_per_kw': solar.inverter_cost_per_kw, 
    # Battery costs
    'battery_cost_per_kWh': battery.cost_per_kwh,
    'battery_annual_maintenance_cost': battery.annual_maintenance_cost,
    'battery_residual_value_factor': battery.residual_value_factor,
    'depth_of_discharge': battery.depth_of_discharge,
    # Battery specs
    'battery_charging_efficiency': battery.charging_efficiency,
    'battery_discharging_efficiency': battery.discharging_efficiency,
    #'battery_annual_degradation': battery.annual_degradation, # 2% per year
    'battery_duration': battery.duration, 
    'battery_max_cycles': battery.max_cycles,
    'battery_end_of_life_perc': battery.end_of_life_perc,
    'battery_trickle_charging_rate': battery.trickle_charging_rate,
    'battery_lifetime_years': battery.lifetime_years,
    'enable_trickle_charging': False,
    'repurchase_battery': True,
    'limit_battery_repurchases': False,
    # Energy costs and schedule 
    'time_of_use_tariffs_high': market.time_of_use_tariffs_high,
    'time_of_use_tariffs_low': market.time_of_use_tariffs_low,
    'high_period_start': market.high_period_start,
    'high_period_end': market.high_period_end,
    'time_periods': market.time_periods,
    'feed_in_tariff': market.feed_in_tariff,
    # Market inputs 
    'interest rate': market.interest_rate,
    'inflation rate': market.inflation_rate,
    'discount rate': market.discount_rate,
    'cost_diesel': market.cost_diesel,
    # Vehicle specs
    'L_km': market.L_km, 
    'kwh_km': market.kwh_km,
    'hiring_cost': market.hiring_cost,
    # Load shedding 
  #  'load_shedding_bool': False,
    'load_shedding_schedule': ls_annual_empty,
    'full_ev_fleet': True,
    # Loan model
  #  'loan_payback_period': market.loan_payback_period,
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
