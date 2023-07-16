import numpy as np
import pandas as pd
from pyomo.opt import SolverFactory
from pyomo.core import Var
import pyomo.environ as en


class Battery(object):
    """ Used to store information about the battery.

       :param current_charge: is the initial state of charge of the battery
       :param capacity: is the battery capacity in Wh
       :param charging_power_limit: the limit of the power that can charge the battery in W
       :param discharging_power_limit: the limit of the power that can discharge the battery in W
       :param battery_charging_efficiency: The efficiecny of the battery when charging
       :param battery_discharing_efficiecny: The discharging efficiency
    """
    def __init__(self,
                 current_charge=0.0,
                 capacity=0.0,
                 charging_power_limit=1.0,
                 discharging_power_limit=-1.0,
                 charging_efficiency=0.95,
                 discharging_efficiency=0.95):
        self.current_charge = current_charge
        self.capacity = capacity
        self.charging_power_limit = charging_power_limit
        self.discharging_power_limit = discharging_power_limit
        self.charging_efficiency = charging_efficiency
        self.discharging_efficiency = discharging_efficiency



    
def schedule_battery_usage(load_profile, pv_output_profile, 
                             battery_capacity, battery_duration,
                             charging_efficiency, discharging_efficiency,
                             buyPrice, sellPrice):
    

    batt = Battery(current_charge=0.0,
                   capacity = battery_capacity,
                   charging_efficiency = charging_efficiency,
                   discharging_efficiency = discharging_efficiency,
                   charging_power_limit = battery_capacity/battery_duration,
                   discharging_power_limit = -battery_capacity/battery_duration)
                   
    # Calculate net load profile and get positive and negative load arrays 
    net_load_profile = [load - pv for load,pv in zip(load_profile ,pv_output_profile)] 
    
    # split load into +ve and -ve
    posLoad = np.copy(net_load_profile)
    negLoad = np.copy(net_load_profile)
    for j,e in enumerate(net_load_profile):
        if e>=0:
            negLoad[j]=0
        else:
            posLoad[j]=0
    posLoadDict = dict(enumerate(posLoad))
    negLoadDict = dict(enumerate(negLoad))
    
    
    ## Get buy and sell price dicts
    priceDict1 = dict(enumerate(sellPrice))
    priceDict2 = dict(enumerate(buyPrice))
    
    

    # now set up the pyomo model
    m = en.ConcreteModel()

    # we use rangeset to make a sequence of integers
    # time is what we will use as the model index
    m.Time = en.RangeSet(0, len(net_load_profile)-1)

    # variables (all indexed by Time)
    m.SOC = en.Var(m.Time, bounds=(0,batt.capacity), initialize=0) #0
    m.posDeltaSOC = en.Var(m.Time, initialize=0) #1
    m.negDeltaSOC = en.Var(m.Time, initialize=0) #2
    m.posEInGrid = en.Var(m.Time, bounds=(0,batt.charging_power_limit*(15/60.)), initialize=0) #3
    m.posEInPV = en.Var(m.Time, bounds=(0,batt.charging_power_limit*(15/60.)), initialize=0) #4
    m.negEOutLocal = en.Var(m.Time, bounds=(batt.discharging_power_limit*(15/60.),0), initialize=0) #5
    m.negEOutExport = en.Var(m.Time, bounds=(batt.discharging_power_limit*(15/60.),0), initialize=0) #6
    m.posNetLoad = en.Var(m.Time, initialize=posLoadDict) #7
    m.negNetLoad = en.Var(m.Time, initialize=negLoadDict) #8

    # Boolean variables (again indexed by Time)
    m.Bool_char=en.Var(m.Time,within=en.Boolean) #9
    m.Bool_dis=en.Var(m.Time,within=en.Boolean,initialize=0) #10

    # parameters (indexed by time)
    m.priceSell = en.Param(m.Time, initialize=priceDict1)
    m.priceBuy = en.Param(m.Time, initialize=priceDict2)
    m.posLoad = en.Param(m.Time, initialize=posLoadDict)
    m.negLoad = en.Param(m.Time, initialize=negLoadDict)

    # single value parameters
    m.etaChg = en.Param(initialize = batt.charging_efficiency)
    m.etaDisChg = en.Param(initialize = batt.discharging_efficiency)
    m.ChargingLimit = en.Param(initialize = batt.charging_power_limit*(15/60.))
    m.DischargingLimit = en.Param(initialize = batt.discharging_power_limit*(15/60.))
    
    
    # objective function
    def Obj_fn(m):
        return sum((m.priceBuy[i]*m.posNetLoad[i]) + (m.priceSell[i]*m.negNetLoad[i]) for i in m.Time)  
    m.total_cost = en.Objective(rule=Obj_fn,sense=en.minimize)
    
    
        # constraints
    # first we define the constraint at each time period
    def SOC_rule(m,t):
        if t==0:
            return (m.SOC[t] == m.posDeltaSOC[t]+m.negDeltaSOC[t])
        else:
            return (m.SOC[t] == m.SOC[t-1]+m.posDeltaSOC[t]+m.negDeltaSOC[t])   
    # then we specify that this constraint is indexed by time
    m.Batt_SOC = en.Constraint(m.Time,rule=SOC_rule)


    # we use bigM to bound the problem
    # boolean constraints
    def Bool_char_rule_1(m,i):
        bigM=500000
        return((m.posDeltaSOC[i])>=-bigM*(m.Bool_char[i]))
    m.Batt_ch1=en.Constraint(m.Time,rule=Bool_char_rule_1)
    # if battery is charging, charging must be greater than -large
    # if not, charging geq zero
    def Bool_char_rule_2(m,i):
        bigM=500000
        return((m.posDeltaSOC[i])<=0+bigM*(1-m.Bool_dis[i]))
    m.Batt_ch2=en.Constraint(m.Time,rule=Bool_char_rule_2)
    # if batt discharging, charging must be leq zero
    # if not, charging leq +large
    def Bool_char_rule_3(m,i):
        bigM=500000
        return((m.negDeltaSOC[i])<=bigM*(m.Bool_dis[i]))
    m.Batt_cd3=en.Constraint(m.Time,rule=Bool_char_rule_3)
    # if batt discharge, discharge leq POSITIVE large
    # if not, discharge leq 0
    def Bool_char_rule_4(m,i):
        bigM=500000
        return((m.negDeltaSOC[i])>=0-bigM*(1-m.Bool_char[i]))
    m.Batt_cd4=en.Constraint(m.Time,rule=Bool_char_rule_4)
    # if batt charge, discharge geq zero
    # if not, discharge geq -large
    def Batt_char_dis(m,i):
        return (m.Bool_char[i]+m.Bool_dis[i],1)
    m.Batt_char_dis=en.Constraint(m.Time,rule=Batt_char_dis)
    
    
    #ensure charging efficiency is divided
    def pos_E_in_rule(m,i):
        return (m.posEInGrid[i]+m.posEInPV[i]) == m.posDeltaSOC[i]/m.etaChg
    m.posEIn_cons = en.Constraint(m.Time, rule=pos_E_in_rule)
    # ensure discharging eff multiplied
    def neg_E_out_rule(m,i):
        return (m.negEOutLocal[i]+m.negEOutExport[i]) == m.negDeltaSOC[i]*m.etaDisChg
    m.negEOut_cons = en.Constraint(m.Time, rule=neg_E_out_rule)

    # ensure charging rate obeyed
    def E_charging_rate_rule(m,i):
        return (m.posEInGrid[i]+m.posEInPV[i])<=m.ChargingLimit
    m.chargingLimit_cons = en.Constraint(m.Time, rule=E_charging_rate_rule)
    # ensure DIScharging rate obeyed
    def E_discharging_rate_rule(m,i):
        return (m.negEOutLocal[i]+m.negEOutExport[i])>=m.DischargingLimit
    m.dischargingLimit_cons = en.Constraint(m.Time, rule=E_discharging_rate_rule)

    # ensure that posEInPV cannot exceed local PV
    def E_solar_charging_rule(m,i):
        return m.posEInPV[i]<=-m.negLoad[i]
    m.solarChargingLimit_cons = en.Constraint(m.Time, rule=E_solar_charging_rule)
    # ensure that negEOutLocal cannot exceed local demand
    def E_local_discharge_rule(m,i):
        return m.negEOutLocal[i]>=-m.posLoad[i]
    m.localDischargingLimit_cons = en.Constraint(m.Time, rule=E_local_discharge_rule)

    # calculate the net positive demand
    def E_pos_net_rule(m,i):
        return m.posNetLoad[i] == m.posLoad[i]+m.posEInGrid[i]+m.negEOutLocal[i]
    m.E_posNet_cons = en.Constraint(m.Time,rule=E_pos_net_rule)

    # calculate export
    def E_neg_net_rule(m,i):
        return m.negNetLoad[i] == m.negLoad[i]+m.posEInPV[i]+m.negEOutExport[i]
    m.E_negNet_cons = en.Constraint(m.Time,rule=E_neg_net_rule)
    
    #opt = SolverFactory("gurobi", executable= "/usr/local/bin/gurobi_cl")
    opt = SolverFactory("glpk", executable= "/usr/local/bin/glpsol")
    
    results = opt.solve(m)
    
    # now let's read in the value for each of the variables 
    outputVars = np.zeros((9,len(sellPrice)))
    
    
    j = 0
    for v in m.component_objects(Var, active=True):
        print( v.getname())
        
        varobject = getattr(m, str(v))
        print (varobject.get_values())
        for index in varobject:
            outputVars[j,index] = varobject[index].value
        j+=1
        if j>=9:
            break
        
    newNetLoad = outputVars[7]+outputVars[8]
    
    return newNetLoad 