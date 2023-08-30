
# Solar PV cost
# panel_wattage = 415 # Rand
# cost_per_panel = 2633.35 # Rand
# cost_per_watt = cost_per_panel / panel_wattage
#cost_per_kw = cost_per_watt * 1000 # R/kW

cost_per_kw = 400 # USD

# Inverter
inverter_cost_per_kw = 0.20 * cost_per_kw 

# Maintenance cost 
annual_maintenance_cost = 25 # $/kW

# Security cost???
annual_security_cost = 0  #$/kW

# PV system specifications
m_sq_per_kw = 2/0.465 # m^2/kW
Rproj = 25 # project lifetime (yrs)
annual_degradation = 0.006 # 0.6% degradation per year

# Residual value
residual_value_factor = 0.10 # %
