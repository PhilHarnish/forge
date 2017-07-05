from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Zebra puzzle', SOURCE)


SOURCE = """
# There are five houses.
position <= {1, 2, 3, 4, 5}
color <= {Yellow, Blue, Red, Ivory, Green}
animal <= {Fox, Horse, Snails, Dog, Zebra}
cigarette <= {Kools, Chesterfields, 'Old Gold', 'Lucky Strike', Parliaments}
drink <= {Water, Tea, Milk, 'Orange Juice', Coffee}
nationality <= {Norwegian, Ukrainian, Englishman, Spaniard, Japanese}
# The Englishman lives in the red house.
Englishman == Red
# The Spaniard owns the dog.
Spaniard == Dog
# Coffee is drunk in the green house.
Coffee == Green
# The Ukrainian drinks tea.
Ukrainian == Tea
# The green house is immediately to the right of the ivory house.
# The Old Gold smoker owns snails.
Old_Gold == Snails
# Kools are smoked in the yellow house.
Kools == Yellow
# Milk is drunk in the middle house.
Milk == _3
# The Norwegian lives in the first house.
Norwegian == _1
# The man who smokes Chesterfields lives in the house next to the man with the fox.
abs(Chesterfields.position - Fox.position) == 1
# Kools are smoked in the house next to the house where the horse is kept.
abs(Kools.position - Horse.position) == 1
# The Lucky Strike smoker drinks orange juice.
Lucky_Strike == 'Orange Juice'
# The Japanese smokes Parliaments.
Japanese == Parliaments
# The Norwegian lives next to the blue house.
abs(Norwegian.position - Blue.position) == 1
"""

PARSED = '''
from data.logic.dsl import *
dimensions = DimensionFactory()
model = Model(dimensions)
"""# There are five houses."""
_1, _2, _3, _4, _5 = position = dimensions(position=[1, 2, 3, 4, 5])
yellow, blue, red, ivory, green = color = dimensions(color=['Yellow',
    'Blue', 'Red', 'Ivory', 'Green'])
fox, horse, snails, dog, zebra = animal = dimensions(animal=['Fox', 'Horse',
    'Snails', 'Dog', 'Zebra'])
kools, chesterfields, old_gold, lucky_strike, parliaments = cigarette = (
    dimensions(cigarette=['Kools', 'Chesterfields', 'Old Gold',
    'Lucky Strike', 'Parliaments']))
water, tea, milk, orange_juice, coffee = drink = dimensions(drink=['Water',
    'Tea', 'Milk', 'Orange Juice', 'Coffee'])
norwegian, ukrainian, englishman, spaniard, japanese = nationality = (
    dimensions(nationality=['Norwegian', 'Ukrainian', 'Englishman',
    'Spaniard', 'Japanese']))
"""# The Englishman lives in the red house."""
model(englishman == red)
"""# The Spaniard owns the dog."""
model(spaniard == dog)
"""# Coffee is drunk in the green house."""
model(coffee == green)
"""# The Ukrainian drinks tea."""
model(ukrainian == tea)
"""# The green house is immediately to the right of the ivory house."""
"""# The Old Gold smoker owns snails."""
model(old_gold == snails)
"""# Kools are smoked in the yellow house."""
model(kools == yellow)
"""# Milk is drunk in the middle house."""
model(milk == _3)
"""# The Norwegian lives in the first house."""
model(norwegian == _1)
"""# The man who smokes Chesterfields lives in the house next to the man with the fox."""
model(abs(chesterfields.position - fox.position) == 1)
"""# Kools are smoked in the house next to the house where the horse is kept."""
model(abs(kools.position - horse.position) == 1)
"""# The Lucky Strike smoker drinks orange juice."""
model(lucky_strike == orange_juice)
"""# The Japanese smokes Parliaments."""
model(japanese == parliaments)
"""# The Norwegian lives next to the blue house."""
model(abs(norwegian.position - blue.position) == 1)
'''

SOLUTION = """
Left	Yellow	Fox	Kools	Water	Norwegian
Middle left	Blue	Horse	Chesterfields	Tea	Ukrainian
Middle	Red	Snails	Old Gold	Milk	Englishman
Middle right	Ivory	Dog	Lucky Strike	Orange Juice	Spaniard
Right	Green	Zebra	Parliaments	Coffee	Japanese
"""
