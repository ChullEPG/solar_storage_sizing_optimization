
# Solar PV cost
panel_wattage = 415 # Rand
cost_per_panel = 2633.35 # Rand
cost_per_watt = cost_per_panel / panel_wattage
cost_per_kw = cost_per_watt * 1000 # R/kW

# Inverter
inverter_cost_per_kw = 0.20 * cost_per_kw 

# # Components cost
# component_cost_per_kw = inverter_cost_per_kw + cost_per_kw # $/kW

# # Other costs
# peripherals_cost_per_kw = component_cost_per_kw * 0.20 # $/kW
# installation_cost_per_kw = (component_cost_per_kw + peripherals_cost_per_kw) * 0.10 # $/kW
# markup_cost = (component_cost_per_kw + peripherals_cost_per_kw + installation_cost_per_kw) * 0.33 # $/kW

# # Total capital cost
# total_cost_per_kw = component_cost_per_kw + peripherals_cost_per_kw + installation_cost_per_kw + markup_cost # $/kW

# Maintenance cost 
annual_maintenance_cost = 200 # $/kW

# PV system specifications
efficiency = 0.90  # 85% efficiency
m_sq_per_kw = 2/0.465 # m^2/kW
Rproj = 25 # project lifetime (yrs)
annual_degradation = 0.006 # 0.6% degradation per year

# Residual value
residual_value_factor = 0.10 # %

