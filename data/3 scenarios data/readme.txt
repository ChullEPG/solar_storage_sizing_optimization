All electric vehicles have the following specs:
- 70kwh battery
- 22kw charging rate
- 0.55kwh/km efficiency

In all instances, there are as many chargers as electric vehicles.

The algorithm settings are as follows:
- ice vehicles are set to greedy (first in queue if closest)
- trips were assigned to lowest SOC vehicle (if the same distance and still feasible)
- chargers were assigned to highest SOC vehicle (no influence because always had enough chargers)
- vehicles were allowed a max time of 30 MINUTES at a non-depot location before having to return back