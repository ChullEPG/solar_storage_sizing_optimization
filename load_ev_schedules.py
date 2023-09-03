from read_ev_schedules import * 


################################################ Mixed fleet no load shedding ################################################

# Processing Weekly schedules
mon_fri_25_perc_ev = pd.concat([process_ev_schedule_data('data/3 scenarios data/ev_penetration/m-f/19,28.txt')]*5, ignore_index = True)
mon_fri_50_perc_ev = pd.concat([process_ev_schedule_data('data/3 scenarios data/ev_penetration/m-f/38,9.txt')]*5, ignore_index = True)
mon_fri_75_perc_ev = pd.concat([process_ev_schedule_data('data/3 scenarios data/ev_penetration/m-f/57,0.txt')]*5, ignore_index = True)
mon_fri_100_perc_ev = pd.concat([process_ev_schedule_data('data/3 scenarios data/ev_penetration/m-f/76,0.txt')]*5, ignore_index = True)

# Processing Saturday schedules 
sat_25_perc_ev = process_ev_schedule_data('data/3 scenarios data/ev_penetration/sat/19,38.txt')
sat_50_perc_ev = process_ev_schedule_data('data/3 scenarios data/ev_penetration/sat/38,23.txt')
sat_75_perc_ev = process_ev_schedule_data('data/3 scenarios data/ev_penetration/sat/57,10.txt')
sat_100_perc_ev = process_ev_schedule_data('data/3 scenarios data/ev_penetration/sat/76,0.txt')

# Processing Sunday schedules
sun_25_perc_ev = process_ev_schedule_data('data/3 scenarios data/ev_penetration/sun/19,21.txt')
sun_50_perc_ev = process_ev_schedule_data('data/3 scenarios data/ev_penetration/sun/38,8.txt')
sun_75_perc_ev = process_ev_schedule_data('data/3 scenarios data/ev_penetration/sun/57,0.txt')
sun_100_perc_ev = process_ev_schedule_data('data/3 scenarios data/ev_penetration/sun/76,0.txt')

# Concatenating into full weekly charging profiles
weekly_25_perc_ev = pd.concat([mon_fri_25_perc_ev, sat_25_perc_ev, sun_25_perc_ev], ignore_index = True)
weekly_50_perc_ev = pd.concat([mon_fri_50_perc_ev, sat_50_perc_ev, sun_50_perc_ev], ignore_index = True)
weekly_75_perc_ev = pd.concat([mon_fri_75_perc_ev, sat_75_perc_ev, sun_75_perc_ev], ignore_index = True)
weekly_100_perc_ev = pd.concat([mon_fri_100_perc_ev, sat_100_perc_ev, sun_100_perc_ev], ignore_index = True)

# Converting to annual charging profiles
annual_25_perc_ev = pd.concat([pd.concat([weekly_25_perc_ev] * 52, ignore_index=True), sat_25_perc_ev], ignore_index=True)
annual_50_perc_ev = pd.concat([pd.concat([weekly_50_perc_ev] * 52, ignore_index=True), sat_50_perc_ev], ignore_index=True)
annual_75_perc_ev = pd.concat([pd.concat([weekly_75_perc_ev] * 52, ignore_index=True), sat_75_perc_ev], ignore_index=True)
annual_100_perc_ev = pd.concat([pd.concat([weekly_100_perc_ev] * 52, ignore_index=True), sat_100_perc_ev], ignore_index=True)

# Downsample from minutely to hourly
annual_25_perc_ev = downsample_minutely_to_hourly(annual_25_perc_ev)
annual_50_perc_ev = downsample_minutely_to_hourly(annual_50_perc_ev)
annual_75_perc_ev = downsample_minutely_to_hourly(annual_75_perc_ev)
annual_100_perc_ev = downsample_minutely_to_hourly(annual_100_perc_ev)

# write files
np.savetxt(f"processed_ev_schedule_data/annual_25_perc_ev.txt", annual_25_perc_ev)
np.savetxt(f"processed_ev_schedule_data/annual_50_perc_ev.txt", annual_50_perc_ev)
np.savetxt(f"processed_ev_schedule_data/annual_75_perc_ev.txt", annual_75_perc_ev)
np.savetxt(f"processed_ev_schedule_data/annual_100_perc_ev.txt", annual_100_perc_ev)


######################################################################################################################################################
##################################### 25 % penetration w/ load shedding #############################################################

# Processing Weekly schedules (note- only taking first day of week for each of these so that can append them together in desired order)
mon_fri_ls_1_25_perc_pen  = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/19/m-f/ls_pattern=0.txt')]*5, ignore_index = True)[0:1440]
mon_fri_ls_2_25_perc_pen = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/19/m-f/ls_pattern=1.txt')]*5, ignore_index = True)[0:1440]
mon_fri_ls_3_25_perc_pen  = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/19/m-f/ls_pattern=2.txt')]*5, ignore_index = True)[0:1440]
mon_fri_ls_4_25_perc_pen  = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/19/m-f/ls_pattern=3.txt')]*5, ignore_index = True)[0:1440]

# Processing Saturday schedules 
sat_ls_1_25_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/19/sat/ls_pattern=0.txt')
sat_ls_2_25_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/19/sat/ls_pattern=1.txt')
sat_ls_3_25_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/19/sat/ls_pattern=2.txt')
sat_ls_4_25_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/19/sat/ls_pattern=3.txt')

# Processing Sunday schedules
sun_ls_1_25_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/19/sun/ls_pattern=0.txt')
sun_ls_2_25_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/19/sun/ls_pattern=1.txt')
sun_ls_3_25_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/19/sun/ls_pattern=2.txt')
sun_ls_4_25_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/19/sun/ls_pattern=3.txt')

# Concatenating into full weekly charging profiles
weekly_ls_1_25_perc_pen = pd.concat([mon_fri_ls_1_25_perc_pen, mon_fri_ls_2_25_perc_pen, mon_fri_ls_3_25_perc_pen, mon_fri_ls_4_25_perc_pen, mon_fri_ls_1_25_perc_pen, sat_ls_2_25_perc_pen, sun_ls_3_25_perc_pen], ignore_index = True)
# weekly_ls_2 = pd.concat([mon_fri_ls_2, sat_ls_2, sun_ls_2], ignore_index = True)
# weekly_ls_3 = pd.concat([mon_fri_ls_3, sat_ls_3, sun_ls_3], ignore_index = True)
# weekly_ls_4 = pd.concat([mon_fri_ls_4, sat_ls_4, sun_ls_4], ignore_index = True)

# Converting to annual charging profiles
annual_ls_1_25_perc_pen = pd.concat([pd.concat([weekly_ls_1_25_perc_pen] * 52, ignore_index=True), sat_ls_1_25_perc_pen], ignore_index=True)
# annual_ls_2 = pd.concat([pd.concat([weekly_ls_2] * 52, ignore_index=True), sat_ls_2], ignore_index=True)
# annual_ls_3 = pd.concat([pd.concat([weekly_ls_3] * 52, ignore_index=True), sat_ls_3], ignore_index=True)
# annual_ls_4 = pd.concat([pd.concat([weekly_ls_4] * 52, ignore_index=True), sat_ls_4], ignore_index=True)

# Downsample from minutely to hourly
annual_ls_1_25_perc_pen = downsample_minutely_to_hourly(annual_ls_1_25_perc_pen)
# annual_ls_2 = downsample_minutely_to_hourly(annual_ls_2)
# annual_ls_3 = downsample_minutely_to_hourly(annual_ls_3)
# annual_ls_4 = downsample_minutely_to_hourly(annual_ls_4)


# write files
np.savetxt(f"processed_ev_schedule_data/25_perc/weekly_ls_1.txt", weekly_ls_1_25_perc_pen)
np.savetxt(f"processed_ev_schedule_data/25_perc/annual_ls_1.txt", annual_ls_1_25_perc_pen)

######################################################################################################################################################
##################################### 50 % penetration w/ load shedding #############################################################



# Processing Weekly schedules (note- only taking first day of week for each of these so that can append them together in desired order)
mon_fri_ls_1_50_perc_pen  = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/38/m-f/ls_pattern=0.txt')]*5, ignore_index = True)[0:1440]
mon_fri_ls_2_50_perc_pen = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/38/m-f/ls_pattern=1.txt')]*5, ignore_index = True)[0:1440]
mon_fri_ls_3_50_perc_pen  = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/38/m-f/ls_pattern=2.txt')]*5, ignore_index = True)[0:1440]
mon_fri_ls_4_50_perc_pen  = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/38/m-f/ls_pattern=3.txt')]*5, ignore_index = True)[0:1440]

# Processing Saturday schedules 
sat_ls_1_50_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/38/sat/ls_pattern=0.txt')
sat_ls_2_50_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/38/sat/ls_pattern=1.txt')
sat_ls_3_50_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/38/sat/ls_pattern=2.txt')
sat_ls_4_50_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/38/sat/ls_pattern=3.txt')

# Processing Sunday schedules
sun_ls_1_50_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/38/sun/ls_pattern=0.txt')
sun_ls_2_50_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/38/sun/ls_pattern=1.txt')
sun_ls_3_50_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/38/sun/ls_pattern=2.txt')
sun_ls_4_50_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/38/sun/ls_pattern=3.txt')

# Concatenating into full weekly charging profiles
weekly_ls_1_50_perc_pen = pd.concat([mon_fri_ls_1_50_perc_pen, mon_fri_ls_2_50_perc_pen, mon_fri_ls_3_50_perc_pen, mon_fri_ls_4_50_perc_pen, mon_fri_ls_1_50_perc_pen, sat_ls_2_50_perc_pen, sun_ls_3_50_perc_pen], ignore_index = True)
# weekly_ls_2 = pd.concat([mon_fri_ls_2, sat_ls_2, sun_ls_2], ignore_index = True)
# weekly_ls_3 = pd.concat([mon_fri_ls_3, sat_ls_3, sun_ls_3], ignore_index = True)
# weekly_ls_4 = pd.concat([mon_fri_ls_4, sat_ls_4, sun_ls_4], ignore_index = True)

# Converting to annual charging profiles
annual_ls_1_50_perc_pen = pd.concat([pd.concat([weekly_ls_1_50_perc_pen] * 52, ignore_index=True), sat_ls_1_50_perc_pen], ignore_index=True)
# annual_ls_2 = pd.concat([pd.concat([weekly_ls_2] * 52, ignore_index=True), sat_ls_2], ignore_index=True)
# annual_ls_3 = pd.concat([pd.concat([weekly_ls_3] * 52, ignore_index=True), sat_ls_3], ignore_index=True)
# annual_ls_4 = pd.concat([pd.concat([weekly_ls_4] * 52, ignore_index=True), sat_ls_4], ignore_index=True)

# Downsample from minutely to hourly
annual_ls_1_50_perc_pen = downsample_minutely_to_hourly(annual_ls_1_50_perc_pen)
# annual_ls_2 = downsample_minutely_to_hourly(annual_ls_2)
# annual_ls_3 = downsample_minutely_to_hourly(annual_ls_3)
# annual_ls_4 = downsample_minutely_to_hourly(annual_ls_4)


# write files
np.savetxt(f"processed_ev_schedule_data/50_perc/weekly_ls_1.txt", weekly_ls_1_50_perc_pen)
np.savetxt(f"processed_ev_schedule_data/50_perc/annual_ls_1.txt", annual_ls_1_50_perc_pen)




######################################################################################################################################################
##################################### 75 % penetration w/ load shedding #############################################################



# Processing Weekly schedules (note- only taking first day of week for each of these so that can append them together in desired order)
mon_fri_ls_1_75_perc_pen  = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/57/m-f/ls_pattern=0.txt')]*5, ignore_index = True)[0:1440]
mon_fri_ls_2_75_perc_pen = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/57/m-f/ls_pattern=1.txt')]*5, ignore_index = True)[0:1440]
mon_fri_ls_3_75_perc_pen  = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/57/m-f/ls_pattern=2.txt')]*5, ignore_index = True)[0:1440]
mon_fri_ls_4_75_perc_pen  = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/57/m-f/ls_pattern=3.txt')]*5, ignore_index = True)[0:1440]

# Processing Saturday schedules 
sat_ls_1_75_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/57/sat/ls_pattern=0.txt')
sat_ls_2_75_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/57/sat/ls_pattern=1.txt')
sat_ls_3_75_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/57/sat/ls_pattern=2.txt')
sat_ls_4_75_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/57/sat/ls_pattern=3.txt')

# Processing Sunday schedules
sun_ls_1_75_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/57/sun/ls_pattern=0.txt')
sun_ls_2_75_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/57/sun/ls_pattern=1.txt')
sun_ls_3_75_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/57/sun/ls_pattern=2.txt')
sun_ls_4_75_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/57/sun/ls_pattern=3.txt')

# Concatenating into full weekly charging profiles
weekly_ls_1_75_perc_pen = pd.concat([mon_fri_ls_1_75_perc_pen, mon_fri_ls_2_75_perc_pen, mon_fri_ls_3_75_perc_pen, mon_fri_ls_4_75_perc_pen, mon_fri_ls_1_75_perc_pen, sat_ls_2_75_perc_pen, sun_ls_3_75_perc_pen], ignore_index = True)
# weekly_ls_2 = pd.concat([mon_fri_ls_2, sat_ls_2, sun_ls_2], ignore_index = True)
# weekly_ls_3 = pd.concat([mon_fri_ls_3, sat_ls_3, sun_ls_3], ignore_index = True)
# weekly_ls_4 = pd.concat([mon_fri_ls_4, sat_ls_4, sun_ls_4], ignore_index = True)

# Converting to annual charging profiles
annual_ls_1_75_perc_pen = pd.concat([pd.concat([weekly_ls_1_75_perc_pen] * 52, ignore_index=True), sat_ls_1_75_perc_pen], ignore_index=True)
# annual_ls_2 = pd.concat([pd.concat([weekly_ls_2] * 52, ignore_index=True), sat_ls_2], ignore_index=True)
# annual_ls_3 = pd.concat([pd.concat([weekly_ls_3] * 52, ignore_index=True), sat_ls_3], ignore_index=True)
# annual_ls_4 = pd.concat([pd.concat([weekly_ls_4] * 52, ignore_index=True), sat_ls_4], ignore_index=True)

# Downsample from minutely to hourly
annual_ls_1_75_perc_pen = downsample_minutely_to_hourly(annual_ls_1_75_perc_pen)
# annual_ls_2 = downsample_minutely_to_hourly(annual_ls_2)
# annual_ls_3 = downsample_minutely_to_hourly(annual_ls_3)
# annual_ls_4 = downsample_minutely_to_hourly(annual_ls_4)


# write files
np.savetxt(f"processed_ev_schedule_data/75_perc/weekly_ls_1.txt", weekly_ls_1_75_perc_pen)
np.savetxt(f"processed_ev_schedule_data/75_perc/annual_ls_1.txt", annual_ls_1_75_perc_pen)





######################################################################################################################################################
##################################### 75 % penetration w/ load shedding #############################################################



# Processing Weekly schedules (note- only taking first day of week for each of these so that can append them together in desired order)
mon_fri_ls_1_100_perc_pen  = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/76/m-f/ls_pattern=0.txt')]*5, ignore_index = True)[0:1440]
mon_fri_ls_2_100_perc_pen = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/76/m-f/ls_pattern=1.txt')]*5, ignore_index = True)[0:1440]
mon_fri_ls_3_100_perc_pen  = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/76/m-f/ls_pattern=2.txt')]*5, ignore_index = True)[0:1440]
mon_fri_ls_4_100_perc_pen  = pd.concat([process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/76/m-f/ls_pattern=3.txt')]*5, ignore_index = True)[0:1440]

# Processing Saturday schedules 
sat_ls_1_100_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/76/sat/ls_pattern=0.txt')
sat_ls_2_100_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/76/sat/ls_pattern=1.txt')
sat_ls_3_100_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/76/sat/ls_pattern=2.txt')
sat_ls_4_100_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/76/sat/ls_pattern=3.txt')

# Processing Sunday schedules
sun_ls_1_100_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/76/sun/ls_pattern=0.txt')
sun_ls_2_100_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/76/sun/ls_pattern=1.txt')
sun_ls_3_100_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/76/sun/ls_pattern=2.txt')
sun_ls_4_100_perc_pen = process_ev_schedule_data('data/3 scenarios data/2hrs_ls/2hr_ls_mixed_fleet_all_percentages/76/sun/ls_pattern=3.txt')

# Concatenating into full weekly charging profiles
weekly_ls_1_100_perc_pen = pd.concat([mon_fri_ls_1_100_perc_pen, mon_fri_ls_2_100_perc_pen, mon_fri_ls_3_100_perc_pen, mon_fri_ls_4_100_perc_pen, mon_fri_ls_1_100_perc_pen, sat_ls_2_100_perc_pen, sun_ls_3_100_perc_pen], ignore_index = True)
# weekly_ls_2 = pd.concat([mon_fri_ls_2, sat_ls_2, sun_ls_2], ignore_index = True)
# weekly_ls_3 = pd.concat([mon_fri_ls_3, sat_ls_3, sun_ls_3], ignore_index = True)
# weekly_ls_4 = pd.concat([mon_fri_ls_4, sat_ls_4, sun_ls_4], ignore_index = True)

# Converting to annual charging profiles
annual_ls_1_100_perc_pen = pd.concat([pd.concat([weekly_ls_1_100_perc_pen] * 52, ignore_index=True), sat_ls_1_100_perc_pen], ignore_index=True)
# annual_ls_2 = pd.concat([pd.concat([weekly_ls_2] * 52, ignore_index=True), sat_ls_2], ignore_index=True)
# annual_ls_3 = pd.concat([pd.concat([weekly_ls_3] * 52, ignore_index=True), sat_ls_3], ignore_index=True)
# annual_ls_4 = pd.concat([pd.concat([weekly_ls_4] * 52, ignore_index=True), sat_ls_4], ignore_index=True)

# Downsample from minutely to hourly
annual_ls_1_100_perc_pen = downsample_minutely_to_hourly(annual_ls_1_100_perc_pen)
# annual_ls_2 = downsample_minutely_to_hourly(annual_ls_2)
# annual_ls_3 = downsample_minutely_to_hourly(annual_ls_3)
# annual_ls_4 = downsample_minutely_to_hourly(annual_ls_4)


# write files
np.savetxt(f"processed_ev_schedule_data/100_perc/weekly_ls_1.txt", weekly_ls_1_100_perc_pen)
np.savetxt(f"processed_ev_schedule_data/100_perc/annual_ls_1.txt", annual_ls_1_100_perc_pen)



######################################################################################################################################################
####################################  Bigger battery on the EVs now ############################################################
######################################################################################################################################################


# Processing Weekly schedules
mon_fri_ls_1_ev_only = pd.concat([process_ev_schedule_data('data/3 scenarios data/ls_only_ev_bigger_battery/m_f_0_ev=63_ice=0_ice_distance=0.txt')]*5, ignore_index = True)
mon_fri_ls_2_ev_only= pd.concat([process_ev_schedule_data('data/3 scenarios data/ls_only_ev_bigger_battery/m_f_1_ev=51_ice=0_ice_distance=0.txt')]*5, ignore_index = True)
mon_fri_ls_3_ev_only = pd.concat([process_ev_schedule_data('data/3 scenarios data/ls_only_ev_bigger_battery/m_f_2_ev=50_ice=0_ice_distance=0.txt')]*5, ignore_index = True)
mon_fri_ls_4_ev_only = pd.concat([process_ev_schedule_data('data/3 scenarios data/ls_only_ev_bigger_battery/m_f_3_ev=53_ice=0_ice_distance=0.txt')]*5, ignore_index = True)

# Processing Saturday schedules 
sat_ls_1_ev_only = process_ev_schedule_data('data/3 scenarios data/ls_only_ev_bigger_battery/sat_0_ev=76_battery=100_lateness=0.txt')
sat_ls_2_ev_only = process_ev_schedule_data('data/3 scenarios data/ls_only_ev_bigger_battery/sat_1_ev=73_battery=100_lateness=0.txt')
sat_ls_3_ev_only = process_ev_schedule_data('data/3 scenarios data/ls_only_ev_bigger_battery/sat_2_ev=72_battery=120_lateness=0.txt')
sat_ls_4_ev_only = process_ev_schedule_data('data/3 scenarios data/ls_only_ev_bigger_battery/sat_3_ev=75_battery=131_lateness=0.txt')

# Processing Sunday schedules
sun_ls_1_ev_only = process_ev_schedule_data('data/3 scenarios data/ls_mixed_fleet/sun_0_ev=53_ice=0_ice_distance=0.txt')
sun_ls_2_ev_only = process_ev_schedule_data('data/3 scenarios data/ls_mixed_fleet/sun_1_ev=53_ice=0_ice_distance=0.txt')
sun_ls_3_ev_only = process_ev_schedule_data('data/3 scenarios data/ls_mixed_fleet/sun_2_ev=59_ice=0_ice_distance=0.txt')
sun_ls_4_ev_only = process_ev_schedule_data('data/3 scenarios data/ls_mixed_fleet/sun_3_ev=65_ice=0_ice_distance=0.txt')

# Concatenating into full weekly charging profiles
weekly_ls_1_ev_only = pd.concat([mon_fri_ls_1_ev_only, mon_fri_ls_2_ev_only, mon_fri_ls_3_ev_only, mon_fri_ls_4_ev_only, mon_fri_ls_1_ev_only, sat_ls_2_ev_only, sun_ls_3_ev_only], ignore_index = True)
# weekly_ls_2 = pd.concat([mon_fri_ls_2, sat_ls_2, sun_ls_2], ignore_index = True)
# weekly_ls_3 = pd.concat([mon_fri_ls_3, sat_ls_3, sun_ls_3], ignore_index = True)
# weekly_ls_4 = pd.concat([mon_fri_ls_4, sat_ls_4, sun_ls_4], ignore_index = True)

# Converting to annual charging profiles
annual_ls_1_ev_only = pd.concat([pd.concat([weekly_ls_1_ev_only] * 52, ignore_index=True), sat_ls_1_ev_only], ignore_index=True)
# annual_ls_2 = pd.concat([pd.concat([weekly_ls_2] * 52, ignore_index=True), sat_ls_2], ignore_index=True)
# annual_ls_3 = pd.concat([pd.concat([weekly_ls_3] * 52, ignore_index=True), sat_ls_3], ignore_index=True)
# annual_ls_4 = pd.concat([pd.concat([weekly_ls_4] * 52, ignore_index=True), sat_ls_4], ignore_index=True)

# Downsample from minutely to hourly
annual_ls_1_ev_only = downsample_minutely_to_hourly(annual_ls_1_ev_only)
# annual_ls_2 = downsample_minutely_to_hourly(annual_ls_2)
# annual_ls_3 = downsample_minutely_to_hourly(annual_ls_3)
# annual_ls_4 = downsample_minutely_to_hourly(annual_ls_4)


# write files
np.savetxt(f"processed_ev_schedule_data/annual_ls_1_ev_only.txt", annual_ls_1_ev_only)

