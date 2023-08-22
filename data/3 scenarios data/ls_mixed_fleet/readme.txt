This folder contains all the possible day schedules with stage 4 loadshedding. For each part of the week (M-F,
SAT, SUN), there are schedules for the 4 loadshedding patterns associated with stage 4 loadshedding). In every
case, 76 electric vehicles were made available and if that was not enough, ice vehicles were added until it wasn't
late for any trip.

A NOTE ABOUT SATURDAY, LS_PATTERN 0:
You might wonder, if 76 electric vehicles were made available, why did it not use 3 more electric vehicles
to use one less ice vehicle? The problem is with 9 ice vehicles and 76 electric vehicles it was late for a few
trips (barely though: max lateness of 4min and avg lateness 0.006). The algorithm will use each ice vehicle to
its max, so once it had 10 ice vehicles, it didn't need three of the electric vehicles anymore.

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