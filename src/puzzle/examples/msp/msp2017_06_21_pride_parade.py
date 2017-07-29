from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Pride Parade', SOURCE)


SOURCE = """
position in range(1, 7 + 1)
color in {orange, blue, violet, green, pink, red, yellow}
name in {Phyllis, Patria, Harvey, Courtney, Kimball, Li, Christopher}
direction in {left, right}

def sees(dimension):
  if dimension.left:
    result = dimension.position - 1
  else:
    result = 7 - dimension.position
  return result

# The person in the orange float can see exactly x floats more than Phyllis can, where x is some number.
orange_sees = sees(orange)
phyllis_sees = sees(Phyllis)
orange_sees > phyllis_sees
x = orange_sees - phyllis_sees

# If the blue and violet floats are facing the same direction, then Patria is in one of those floats; otherwise, Patria is in the green float.
if blue.left == violet.left:
  Patria.blue or Patria.violet
else:
  Patria.green
# The person in the blue float can see, directly in front of it, another float whose driver has x letters in his/her name.
# NOTE: Names are 2, 6, 7, 11 so x == 2 or x == 6. 6 is too big for z.
(x == 2)
# If x == 2: blue sees Li.
if blue.left:
  blue[1] == False
  all(Li[i - 1] == blue[i] for i in range(2, 8))
else:
  blue[7] == False
  all(Li[i + 1] == blue[i] for i in range(1, 7))
float_distance = abs(Harvey.position - pink.position) - 1
(float_distance == 2) ^ (float_distance == 4)

# The red float is the farthest west.
red.position[1] == True

# If Courtney’s float is blue, orange, violet, or green, then at least one of Courtney’s neighbors has a name containing the letter Y.
c_is_bovg = (Courtney.blue or Courtney.orange or Courtney.violet or Courtney.green)
c_left_neighbor_has_y = all(Phyllis[i - 1] or Harvey[i - 1] for i in range(2, 8) if Courtney[i])
c_right_neighbor_has_y = all(Phyllis[i + 1] or Harvey[i + 1] for i in range(1, 7) if Courtney[i])
if c_is_bovg:
  c_left_neighbor_has_y or c_right_neighbor_has_y

# Harvey can see Kimball’s float directly in front of him.
if Harvey.left:
  Harvey[1] == False
  all(Kimball[i - 1] for i in range(2, 8) if Harvey[i])
else:
  Harvey[7] == False
  all(Kimball[i + 1] for i in range(1, 7) if Harvey[i])

# The violet float is next to the yellow float if and only if Li’s float is pink.
(Li == pink) == (abs(violet.position - yellow.position) == 1)

# The people in the orange and pink floats can see the blue float somewhere ahead.
blue_left_of_orange = blue.position < orange.position
orange.left == blue_left_of_orange
blue_right_of_orange = blue.position > orange.position
orange.right == blue_right_of_orange
blue_left_of_pink = blue.position < pink.position
pink.left == blue_left_of_pink
blue_right_of_pink = blue.position > pink.position
pink.right == blue_right_of_pink

# If Li’s float is east of Harvey’s, then Li’s float is either orange or pink.
if Li.position > Harvey.position:
  Li.orange or Li.pink

# If Harvey’s float is red or orange, then Kimball’s float is a primary color.
if Harvey.red or Harvey.orange:
  Kimball.red or Kimball.blue

# If the red and yellow floats are next to each other, then the person in the red float can see fewer than y other floats, where y = x + 1.
red_yellow_neighbors = abs(red.position - yellow.position) == 1
red_sees = sees(red)
y = x + 1
if red_yellow_neighbors:
  red_sees < y

# If Christopher’s float is a secondary color, then he can see more floats than Courtney can.
if Christopher.violet or Christopher.orange or Christopher.green:
  sees(Christopher) > sees(Courtney)

# The person in the red float has a name that is z letters long, where z = x * y.
# x = 2 or 6
# y = 3 or 7
# z = 6, 14, 18, 42
# Only "6" works.
z = x * y
(red == Harvey) or (red == Patria)

# The pink, violet, and green floats are facing the same direction.
pink.left == violet.left == violet.left == green.left
"""

SOLUTION = """
position |  color |        name | direction
       1 |    red |      Harvey |     right
       2 |   blue |     Kimball |     right
       3 | orange |          Li |      left
       4 |   pink |    Courtney |      left
       5 | violet | Christopher |      left
       6 |  green |      Patria |      left
       7 | yellow |     Phyllis |     right
"""
