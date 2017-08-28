from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Puzzle 5.3: A Relaxing Brunch', SOURCE)


SOURCE = """
name in {Beth, Charles, David, Frank, Jessica, Karen, Taylor}
# Juice count in #3.
juice in {grapefruit*1, orange*3, prune*1, tomato*2}
# Omlet counts in #4, #5.
omelet in {green*2, jalapeno*1, mushroom*1, seafood*3}
# Pancake counts in #12 and then last two in #10.
pancake in {blueberry, buttermilk*2, chocolate*2, pecan*2}
bread in {muffin, toast}
# Jam counts in #2.
jam in {boysenberry*1, grape*1, raspberry*1, strawberry*4}

#1: <Sets limits which are implied by dimension definitions.>

#2: Regarding 4 strawberry guests.
Jessica != strawberry
# ...this isn't necessary?
all(strawberry[j] == 1 for j in juice)
all(strawberry[o] == 1 for o in omelet)

#3: Regarding 3 OJ.
for p in [buttermilk, chocolate, pecan]:
  orange[p] == 1
orange != blueberry
# FIXME: If Charles gets "orange" it leads to an incorrect solution.
# The issue is very subtle. See:
# https://docs.google.com/spreadsheets/d/16eQ79FXL0GMocV-yvvI4mpVUScklez0a8lbW3U2Oyo4
Charles != orange

#4: Regarding 3 seafood omelets.
seafood.boysenberry == 1
seafood.grape == 1
seafood.toast == 2

#5: Regarding 1 jalapeno omelet, 1 mushroom omelet
jalapeno.muffin == 1
mushroom.toast == 1

#6a: Beth & Taylor had tomato, muffins, ...
for n in (Beth, Taylor):
  n == tomato
  n == muffin
#6b: ...and same omelets.
for o in omelet:
  Beth[o] == Taylor[o]

#7:
prune != seafood

#8:
for o in omelet:
  Jessica[o] == boysenberry[o]

#9:
blueberry.raspberry == 1

#10:
Frank == buttermilk
Frank != grapefruit
grapefruit.buttermilk == 1

#11:
Charles == pecan
Charles != grape
grape.pecan == 1

#12: Pecan and chocolate all had different omelets.
for o in omelet:
  pecan[o] or chocolate[o]

#13a: David and Jessica had muffins...
David == muffin
Jessica == muffin
#13b: ...and only had one other category in common (and it wasn't pancakes).
sum(David[f] and Jessica[f] for f in [orange, tomato, green, seafood, strawberry]) == 1

#14: Beth and Charles agreed in only one category.
# Juice: orange*3 or tomato*2?
# Omelet: green*2 or seafood*3?
# Pancake: buttermilk*2, chocolate*2, pecan*2?
# Bread: muffin, toast?
# Jam: strawberry*4?
sum(Beth[f] and Charles[f] for f in [orange, tomato, green, seafood, buttermilk, chocolate, pecan, muffin, toast, strawberry]) == 1
"""


SOLUTION = """
   name |      juice |   omelet |    pancake |  bread |         jam
   Beth |     tomato |    green |  chocolate | muffin |  strawberry
Charles |      prune | mushroom |      pecan |  toast |  strawberry
  David |     orange | jalapeno |  chocolate | muffin |  strawberry
  Frank |     orange |  seafood | buttermilk |  toast | boysenberry
Jessica |     orange |  seafood |      pecan | muffin |       grape
  Karen | grapefruit |  seafood | buttermilk |  toast |  strawberry
 Taylor |     tomato |    green |  blueberry | muffin |   raspberry
 """
