from puzzle.puzzlepedia import puzzle


def get_houses():
  return puzzle.Puzzle('Very Fun Logic Puzzle', HOUSE_SOURCE)


def get_roses():
  return puzzle.Puzzle('Very Fun Logic Puzzle', ROSE_SOURCE)


HOUSE_SOURCE = """
names <= {
  Abby,
  Charles,
  Danielle,
  Elizabeth,
  Freya,
  Howard,
  Martin,
  Ophelia,
  Philip,
  Rochelle,
  Stuart,
  Thomas,
}
colors <= {
  Black,
  Green,
  Gray,
  Orange,
  Yellow,
  Purple,
  Blue,
  Red,
  Magenta,
  Brown,
  Cyan,
  White,
}

# A Green house is next to a Cyan house.
# Abby shares a picket fence with Charles.
# Both Abby and Danielle live next to the Cyan house.
# Charles and Freya are good friends.
# Elizabeth and Freya like to shout things to each other from their second floor windows.
# Freya is neighbors with Howard and Thomas.
# Gray and Cyan houses appear next to each other.
# Howard lives in the Purple house.
Howard == Purple
# If you lived in the Magenta house, Ophelia would be your neighbor.
# Martin lives next to the Yellow house.
# Only Abby lives in the Black house.
Abby == Black
# Ophelia lives in a lovely, Red Victorian house.
Ophelia == Red
# Orange is next to White.
# People live next to the people they like. They do not live next to people they hate.
# Rochelle and Charles got in a fight years ago and haven't spoken since.
# Stuart loves his Cyan home.
Stuart == Cyan
# Stuart refuses to have anything to do with Howard or Howard's neighbors.
# The Black house is on the opposite side from Elizabeth's house.
# The Brown house is occupied by Rochelle.
Brown == Rochelle
# The Red house neighbors the Gray house, the Cyan house, the house Philip lives in, the Orange house, and the house Thomas lives in.
# The White and Blue houses are not adjacent.
# There is one house of each color, and exactly one person lives in each house.
# You can see the Magenta house from the Brown house.
"""


HOUSE_PARSED = '''
from data.logic.dsl import *
dimensions = DimensionFactory()
model = Model(dimensions)
(abby, charles, danielle, elizabeth, freya, howard, martin, ophelia, philip,
    rochelle, stuart, thomas) = (names) = (dimensions(names=['Abby',
    'Charles', 'Danielle', 'Elizabeth', 'Freya', 'Howard', 'Martin',
    'Ophelia', 'Philip', 'Rochelle', 'Stuart', 'Thomas']))
(black, green, gray, orange, yellow, purple, blue, red, magenta, brown,
    cyan, white) = (colors) = (dimensions(colors=['Black', 'Green', 'Gray',
    'Orange', 'Yellow', 'Purple', 'Blue', 'Red', 'Magenta', 'Brown', 'Cyan',
    'White']))
"""# A Green house is next to a Cyan house."""
"""# Abby shares a picket fence with Charles."""
"""# Both Abby and Danielle live next to the Cyan house."""
"""# Charles and Freya are good friends."""
"""# Elizabeth and Freya like to shout things to each other from their second floor windows."""
"""# Freya is neighbors with Howard and Thomas."""
"""# Gray and Cyan houses appear next to each other."""
"""# Howard lives in the Purple house."""
model(howard == purple)
"""# If you lived in the Magenta house, Ophelia would be your neighbor."""
"""# Martin lives next to the Yellow house."""
"""# Only Abby lives in the Black house."""
model(abby == black)
"""# Ophelia lives in a lovely, Red Victorian house."""
model(ophelia == red)
"""# Orange is next to White."""
"""# People live next to the people they like. They do not live next to people they hate."""
"""# Rochelle and Charles got in a fight years ago and haven't spoken since."""
"""# Stuart loves his Cyan home."""
model(stuart == cyan)
"""# Stuart refuses to have anything to do with Howard or Howard's neighbors."""
"""# The Black house is on the opposite side from Elizabeth's house."""
"""# The Brown house is occupied by Rochelle."""
model(brown == rochelle)
"""# The Red house neighbors the Gray house, the Cyan house, the house Philip lives in, the Orange house, and the house Thomas lives in."""
"""# The White and Blue houses are not adjacent."""
"""# There is one house of each color, and exactly one person lives in each house."""
"""# You can see the Magenta house from the Brown house."""
'''


HOUSE_SOLUTION = """
    names |  colors
     Abby |   Black
  Charles |   White
 Danielle |   Green
Elizabeth | Magenta
    Freya |  Yellow
   Howard |  Purple
   Martin |    Blue
  Ophelia |     Red
   Philip |  Orange
 Rochelle |   Brown
   Stuart |    Cyan
   Thomas |    Gray
"""


# TODO: Cyan.position > Green.position > Orange.position > Black.position > Red.position
ROSE_SOURCE = """
position <= {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14}
color <= {
  Magenta,
  Gray,
  Red,
  Brown,
  Gray,
  Black,
  Gray,
  Purple,
  Blue,
  Orange,
  Green,
  Yellow,
  White,
  Cyan,
}
# A Black rose is surrounded by roses that share a color.
all(Black.position[i] - (Gray.position[i - 1] and Gray.position[i + 1]) <= 0 for i in range(2, 14))
# A Blue rose is no more than two away from a Gray rose.
Blue[2] == False
Blue[13] == False
all(Blue.position[i] - (Gray.position[i - 2] or Gray.position[i - 1] or Gray.position[i + 1] or Gray.position[i + 2]) <= 0 for i in range(3, 13))
# A Magenta rose and a Cyan rose are as far apart as possible.
abs(Magenta.position - Cyan.position) == 14 - 1
# All roses in the right half of the row appear only once in the row.
sum(Gray[i] for i in range(8, 15)) == 0
# Every color of rose, except one, appears exactly once.
# No-op.
# Four roses lie between two Gray roses.
any(Gray.position[i] and Gray.position[i + 5] for i in range(1, 9))
# From right to left, these roses appear in this order, but not necessarily consecutively: Cyan, Green, Orange, Black, Red.
Cyan.position > Green.position
Green.position > Orange.position
Orange.position > Black.position
Black.position > Red.position
# The middle roses are Gray and Purple.
(Gray[7] & Purple[8]) | (Purple[7] & Gray[8])
# The rose in the middle of the left half of the row is Brown.
Brown.position == 4
# The sequence Green, Yellow, White appears somewhere in the row of roses.
Yellow.position - Green.position == 1
White.position - Yellow.position == 1
# There are an even number of roses.
"""


ROSE_PARSED = '''
from data.logic.dsl import *
dimensions = DimensionFactory()
model = Model(dimensions)
_1, _2, _3, _4, _5, _6, _7, _8, _9, _10, _11, _12, _13, _14 = position = (
    dimensions(position=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]))
(magenta, gray, red, brown, gray, black, gray, purple, blue, orange, green,
    yellow, white, cyan) = (color) = (dimensions(color=['Magenta', 'Gray',
    'Red', 'Brown', 'Gray', 'Black', 'Gray', 'Purple', 'Blue', 'Orange',
    'Green', 'Yellow', 'White', 'Cyan']))
"""# A Black rose is surrounded by roses that share a color."""
model(all(black.position[i] - (gray.position[i - 1] & gray.position[i + 1]) <=
    0 for i in range(2, 14)))
"""# A Blue rose is no more than two away from a Gray rose."""
model(blue[2] == False)
model(blue[13] == False)
model(all(blue.position[i] - (gray.position[i - 2] ^ gray.position[i - 1] ^
    gray.position[i + 1] ^ gray.position[i + 2]) <= 0 for i in range(3, 13)))
"""# A Magenta rose and a Cyan rose are as far apart as possible."""
model(abs(magenta.position - cyan.position) == 14 - 1)
"""# All roses in the right half of the row appear only once in the row."""
model(sum(gray[i] for i in range(8, 15)) == 0)
"""# Every color of rose, except one, appears exactly once."""
"""# No-op."""
"""# Four roses lie between two Gray roses."""
model(any(gray.position[i] & gray.position[i + 5] for i in range(1, 9)))
"""# From right to left, these roses appear in this order, but not necessarily consecutively: Cyan, Green, Orange, Black, Red."""
model(cyan.position > green.position)
model(green.position > orange.position)
model(orange.position > black.position)
model(black.position > red.position)
"""# The middle roses are Gray and Purple."""
model(gray[7] & purple[8] | purple[7] & gray[8])
"""# The rose in the middle of the left half of the row is Brown."""
model(brown.position == 4)
"""# The sequence Green, Yellow, White appears somewhere in the row of roses."""
model(yellow.position - green.position == 1)
model(white.position - yellow.position == 1)
"""# There are an even number of roses."""
'''

ROSE_SOLUTION = """
position |   color
       1 | Magenta
       2 |    Gray
       3 |     Red
       4 |   Brown
       5 |    Gray
       6 |   Black
       7 |    Gray
       8 |  Purple
       9 |    Blue
      10 |  Orange
      11 |   Green
      12 |  Yellow
      13 |   White
      14 |    Cyan
"""
