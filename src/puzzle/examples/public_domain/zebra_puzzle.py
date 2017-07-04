from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Zebra puzzle', SOURCE)


SOURCE = """
# There are five houses.
positions <= {Left, 'Middle Left', Middle, 'Middle Right', Right}
colors <= {Yellow, Blue, Red, Ivory, Green}
animals <= {Fox, Horse, Snails, Dog, Zebra}
cigarettes <= {Kools, Chesterfields, 'Old Gold', 'Lucky Strike', Parliaments}
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
Milk == Middle
# The Norwegian lives in the first house.
Norwegian == Left
# The man who smokes Chesterfields lives in the house next to the man with the fox.
# Kools are smoked in the house next to the house where the horse is kept.
# The Lucky Strike smoker drinks orange juice.
Lucky_Strike == 'Orange Juice'
# The Japanese smokes Parliaments.
Japanese == Parliaments
# The Norwegian lives next to the blue house.
"""

PARSED = '''
from data.logic.dsl import *
dimensions = DimensionFactory()
model = Model(dimensions)
"""# There are five houses."""
Left, Middle_Left, Middle, Middle_Right, Right = positions = dimensions(
    positions=['Left', 'Middle Left', 'Middle', 'Middle Right', 'Right'])
Yellow, Blue, Red, Ivory, Green = colors = dimensions(colors=['Yellow',
    'Blue', 'Red', 'Ivory', 'Green'])
Fox, Horse, Snails, Dog, Zebra = animals = dimensions(animals=['Fox',
    'Horse', 'Snails', 'Dog', 'Zebra'])
Kools, Chesterfields, Old_Gold, Lucky_Strike, Parliaments = cigarettes = (
    dimensions(cigarettes=['Kools', 'Chesterfields', 'Old Gold',
    'Lucky Strike', 'Parliaments']))
Water, Tea, Milk, Orange_Juice, Coffee = drink = dimensions(drink=['Water',
    'Tea', 'Milk', 'Orange Juice', 'Coffee'])
Norwegian, Ukrainian, Englishman, Spaniard, Japanese = nationality = (
    dimensions(nationality=['Norwegian', 'Ukrainian', 'Englishman',
    'Spaniard', 'Japanese']))
"""# The Englishman lives in the red house."""
model(Englishman == Red)
"""# The Spaniard owns the dog."""
model(Spaniard == Dog)
"""# Coffee is drunk in the green house."""
model(Coffee == Green)
"""# The Ukrainian drinks tea."""
model(Ukrainian == Tea)
"""# The green house is immediately to the right of the ivory house."""
"""# The Old Gold smoker owns snails."""
model(Old_Gold == Snails)
"""# Kools are smoked in the yellow house."""
model(Kools == Yellow)
"""# Milk is drunk in the middle house."""
model(Milk == Middle)
"""# The Norwegian lives in the first house."""
model(Norwegian == Left)
"""# The man who smokes Chesterfields lives in the house next to the man with the fox."""
"""# Kools are smoked in the house next to the house where the horse is kept."""
"""# The Lucky Strike smoker drinks orange juice."""
model(Lucky_Strike == Orange_Juice)
"""# The Japanese smokes Parliaments."""
model(Japanese == Parliaments)
"""# The Norwegian lives next to the blue house."""
'''

SOLUTION = """
Left	Yellow	Fox	Kools	Water	Norwegian
Middle left	Blue	Horse	Chesterfields	Tea	Ukrainian
Middle	Red	Snails	Old Gold	Milk	Englishman
Middle right	Ivory	Dog	Lucky Strike	Orange Juice	Spaniard
Right	Green	Zebra	Parliaments	Coffee	Japanese
"""
