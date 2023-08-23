
import numpy as np

def get_usable_pv_capacity(pv_capacity, year, a):
    '''
    Linear degradation of PV capacity
    '''
    return pv_capacity * (1 - a['solar_annual_degradation'])**year  
 
def get_usable_battery_capacity(battery_capacity, battery_energy_throughput, battery_max_energy_throughput, year, a):
    '''
    Exponential degradation of battery capacity
    '''
    usable_battery_capacity = battery_capacity - (battery_capacity * (battery_energy_throughput / battery_max_energy_throughput) * (1 - a['battery_end_of_life_perc']))
    return usable_battery_capacity

def get_usable_battery_capacity_v2(battery_capacity, battery_energy_throughput, battery_max_energy_throughput, year, a):
    '''
    Exponential degradation of battery capacity
    '''
    degradation = 1 / (1 + np.exp((battery_max_energy_throughput - battery_energy_throughput) / 1000))
    return battery_capacity - battery_capacity * degradationb