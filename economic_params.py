
# Energy costs and schedule 
rand_to_usd = 1/18.64

time_of_use_tariffs_high = {'peak': 6.97, 'standard': 2.46, 'off_peak': 1.57} 
time_of_use_tariffs_low = {'peak': 2.61, 'standard': 1.95, 'off_peak': 1.42}

# Convert to USD
for key in time_of_use_tariffs_high:
    time_of_use_tariffs_high[key] *= rand_to_usd
    time_of_use_tariffs_low[key] *= rand_to_usd
    
    
high_period_start = 24 * (31 + 28 + 31 + 30 + 31) # 1st hour of June
high_period_end = high_period_start + 24 * (30 + 31 + 31) # 1st hour of November

time_periods = {'peak_hours': [7,8,9,18,19],
                'standard_hours': [6,10,11,12,13,14,15,16,17,20,21],
                'off_peak_hours': [0,1,2,3,4,5,23]}



# Energy market inputs
feed_in_tariff = 0.041 # $/kWh


# Financial market inputs
interest_rate = 0.1175 #  SA interest rate
inflation_rate = 0.0704 # inflation rate
discount_rate = 0.05 # discount rate

# Financing terms
# loan_upfront_adjustment = 0.00 # % of capital cost paid upfront
loan_payback_period = 20 # 10 years for the solar PV system provider to fully recoup their costs
# loan_interest_rate = 0.05

# pays_capital_adjustment = 0.30 # 30% of capital cost paid upfront
# pays_payback_period = 20 # 10 years for the solar PV system provider to fully recoup their costs
# pays_interest_rate = 0.05 # 5% annual interest rate
# pays_cut_of_savings = 0.50 # 50% of savings go to the solar PV system provider

# ICE vehicle specs
kwh_km = 0.55 # kWh/km
L_km = 0.15
km_L = 1/L_km# km/L
kwh_L = kwh_km * km_L # kWh/L

cost_diesel = 1.05 # $/L

# {
#         "time_of_use_tariffs_high": {
#             "peak": 6.97,
#             "standard": 2.46,
#             "off_peak": 1.57
#         },
#         "time_of_use_tariffs_low": {
#             "peak": 2.61,
#             "standard": 1.95,
#             "off_peak": 1.42
#         },
#         "high_period_start": 4008,
#         "high_period_end": 9408,
#         "time_periods": {
#             "peak_hours": [7, 8, 9, 18, 19],
#             "standard_hours": [6, 10, 11, 12, 13, 14, 15, 16, 17, 20, 21],
#             "off_peak_hours": [0, 1, 2, 3, 4, 5, 23]
#         }
#         "feed_in_tariff": 0.041,
#         "i_no": 0.15,
#         "inflation_rate": 0.0704,
#         "discount_rate": 0.05
#         "loan_upfront_adjustment": 0.00,
#         "loan_payback_period": 20,
#         "loan_interest_rate": 0.05,
#         "pays_capital_adjustment": 0.30,
#         "pays_payback_period": 20,
#         "pays_interest_rate": 0.05,
#         "pays_cut_of_savings": 0.50,
#         "kwh_km": 0.70,
#         "L_km": 0.15,
#         "cost_diesel": 1.05
# }
