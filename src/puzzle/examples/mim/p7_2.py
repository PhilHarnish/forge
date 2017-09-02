from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Puzzle 7.2: The Mystery Novels', SOURCE)


SOURCE = """
import itertools
name in {Beth, Charles, David, Frank, Jessica, Karen, Taylor}
novel in {Chair, Folly, Pigeons, Forget, Moon, Nile, Comedy}
rank in range(1, 7+1)

#1:
ages = {
  Beth: variable(30, 60, 'Beth age'),
  Charles: variable(30, 60, 'Charles age'),
  David: variable(30, 60, 'David age'),
  Frank: variable(30, 60, 'Frank age'),
  Jessica: variable(30, 60, 'Jessica age'),
  Karen: variable(30, 60, 'Karen age'),
  Taylor: variable(30, 60, 'Taylor age'),
}
# No longer needed:
# Numberjack.AllDiff([v.value for v in ages.values()])
Beth.rank == sum(ages[Beth] >= a for a in ages.values())
Charles.rank == sum(ages[Charles] >= a for a in ages.values())
David.rank == sum(ages[David] >= a for a in ages.values())
Frank.rank == sum(ages[Frank] >= a for a in ages.values())
Jessica.rank == sum(ages[Jessica] >= a for a in ages.values())
Karen.rank == sum(ages[Karen] >= a for a in ages.values())
Taylor.rank == sum(ages[Taylor] >= a for a in ages.values())

#2: 4th oldest is 48. Satisfied below (see #7, #8).
# any(a == 48 for a in ages.values())
# sum(a > 48 for a in ages.values()) == 3

#3a: Original:
#abs(ages[Jessica] - ages[Taylor]) == 1
#def skip(a, b, x, y):
#  return ((x is ages[a]) and (y is ages[b])) or ((x is ages[b]) and (y is ages[a]))
#
#for a, b in filter(lambda i: skip(Jessica, Taylor, *i) == False, itertools.combinations(ages.values(), 2)):
#  abs(a - b) > 1
#ages[Jessica] <= 50
#ages[Taylor] <= 50
#3b: Simplified given #7, #8:
{Jessica, Taylor} == {2, 3}

#4a: (Original) Frank-Taylor are the widest apart, when sorted by age.
# all(Taylor[i - 1] or Taylor[i + 1] for i in range(2, 6+1) if Frank[i])
# if Frank == 1: Taylor == 2
# if Frank == 7: Taylor == 6
# This implies that any pair of names will be >= that distance.
# ft_diff = abs(ages[Frank] - ages[Taylor])
# Frank <-> Taylor <-> Jessica.
# any(abs(ages[Beth] - ages[a]) < ft_diff for a in [Charles, David, Frank, Jessica, Karen])
# any(abs(ages[Charles] - ages[a]) < ft_diff for a in [Beth, David, Frank, Jessica, Karen])
# any(abs(ages[David] - ages[a]) < ft_diff for a in [Beth, Charles, Frank, Jessica, Karen])
# any(abs(ages[Frank] - ages[a]) < ft_diff for a in [Beth, Charles, David, Karen])
# any(abs(ages[Jessica] - ages[a]) < ft_diff for a in [Beth, Charles, David, Karen])
# any(abs(ages[Karen] - ages[a]) < ft_diff for a in [Beth, Charles, David, Frank, Jessica])
# NB: Skip taylor.
#4b: Simplified given #7, #8:
{Frank, Taylor} == {1, 2}

#5:
{Forget, Comedy} == {1, 2}

#6:
{Chair, Nile} == {6, 7}

#7: There exists a guest who 2/3rds the age of another, also: 3/4, 4/5.
#8: There exists a guest whos age has reversed digits of another.
#all_pairs = list(itertools.combinations(range(30, 60+1), 2))
#targets23 = list(filter(lambda x: x[0] * 3 == x[1] * 2, all_pairs))
#targets34 = list(filter(lambda x: x[0] * 4 == x[1] * 3, all_pairs))
#targets45 = list(filter(lambda x: x[0] * 5 == x[1] * 4, all_pairs))
# All pairs:
# [(30, 45), (32, 48), (34, 51), (36, 54), (38, 57), (40, 60)]
# [(30, 40), (33, 44), (36, 48), (39, 52), (42, 56), (45, 60)]
# [(32, 40), (36, 45),           (40, 50), (44, 55), (48, 60)]
# [          (34, 43),                     (45, 54)          ]  (Rule #8)
# Observations:
# 1. The middle number is 48. Finding 3 pairs with 3 numbers over 48 is not
#    possible unless one of the pairs contains 48.
#    (This is also implied as 48 does not satisfy rule #8).
# 2. If 48 was the larger of the pair then there would not be enough remaining
#    pairs with numbers larger than 48. 48 is the smaller of the pairs.
# >  (48, 60) is one of the pairs.
# 3. With 48 and 60 consumed, these are remaining:
# [(30, 45), (34, 51), (36, 54), (38, 57)    ]
# [(30, 40), (33, 44), (39, 52), (42, 56)    ]
# [                              (48,     60)]
# [          (34, 43),     (45,       54)    ]  (Rule #8)
# 4. There needs to be a pair of numbers <50 per #3. Eliminates:
#    36/54 (no 35, 37)
#    30/40 (no 31, 39, 41)
# [(30, 45), (34, 51), (38, 57)]
# [(33, 44), (39, 52), (42, 56)]
# [                    (48, 60)]
# [(xx, 43), (xx,       54)    ]  (Rule #8)
# 5. If the "reversed digits" was 54 then (30, 45) must be in play. Per #3 that
#    gives: 54 + (30, 45) + (33, 44) and (48, 60).
#           30, 33, 44, 45, 48, 54, 60.
# > ...and 48 is not the 4th oldest.
# >  Reversed digits are "43" which pairs with (34, 51).
# [          (34, 51)          ]
# [(33, 44), (39, 52), (42, 56)]
# [                    (48, 60)]
# [(xx, 43)                    ]  (Rule #8)
# 6. Per #3 that requires (33, 44) or (42, 56).
#    43 + (34, 51) + (33, 44) + (48, 60): Violates #3.
#    43 + (34, 51) + (42, 56) + (48, 60): Okay.
# Sorted: 34, 42, 43, 48, 51, 56, 60.
gcc(ages.values(), {43, 34, 51, 42, 56, 48, 60})
Pigeons != 3

#9:
Beth.rank > Karen.rank
Charles.rank > Karen.rank
Karen.rank > Pigeons.rank

#10:
Taylor != Comedy
Karen != Folly

#11:
Beth.rank < Chair.rank

for k, v in ages.items():
  print(k, v)
"""


SOLUTION = """
   name |   novel | rank
   Beth |    Nile |    6
Charles |   Chair |    7
  David | Pigeons |    4
  Frank |  Comedy |    1
Jessica |   Folly |    3
  Karen |    Moon |    5
 Taylor |  Forget |    2
 """
