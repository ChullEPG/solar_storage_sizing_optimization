This folder contains all the possible day schedules with stage 4 loadshedding for all EV penetration percentages.
For each part of the week (M-F, SAT, SUN), there are schedules for the 4 loadshedding patterns associated with
stage 4 loadshedding).

A NOTE ABOUT SOME OF THE DATA:
In some cases, less EV's were used than what was made available, even when it is using additional ice vehicles to
cover. This behaviour is correct for the current state of the program. If it used one less ICE, it would not have
finished without lateness, but the algorithm is greedy with ICE vehicles, so it maximally uses all it is given, so
now with one ICE more, it uses less EV's

LOADSHEDDING:
All schedules are for stage 4 loadshedding possibilities.
The following are possible schedules for a week, depending what day of the month is the first day of the week.
If this were any other stage, it would have been even more complicated.

MTWTFSS
0000333
0003333
0033332
0333322
3333222
3332222
3322221
3222211
2222111
2221111
2211110
2111100
1111000
1110000
1100003
1000033

So, for example, to calculate a possible week for stage 4 corresponding to the second to last possibility
in the above list, 1100003, you would use the following data to create the week's schedule:
- Monday to Tuesday: use m-f ls_pattern 1
- Wednesday to Friday: use m-f ls_pattern 0
- Saturday: use sat ls_pattern 0
- Sunday: use sun ls_pattern 3