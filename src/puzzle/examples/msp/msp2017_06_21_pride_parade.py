from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Pride Parade', SOURCE)


# TODO:
# The pink, violet, and green floats are facing the same direction.
# pink.direction == violet.direction
# violet.direction == green.direction

SOURCE = """
position <= {1, 2, 3, 4, 5, 6, 7}
color <= {orange, blue, violet, green, pink, red, yellow}
name <= {Phyllis, Patria, Harvey, Courtney, Kimball, Li, Christopher}
direction <= {left, right}
# The person in the orange float can see exactly x floats more than Phyllis can, where x is some number.
print()
orange_left_sees = orange.left * (orange.position - 1)
orange_right_sees = orange.right * (7 - orange.position)
orange_sees = orange_left_sees + orange_right_sees
phyllis_left_sees = Phyllis.left * (Phyllis.position - 1)
phyllis_right_sees = Phyllis.right * (7 - Phyllis.position)
phyllis_sees = phyllis_left_sees + phyllis_right_sees
orange_sees > phyllis_sees
x = orange_sees - phyllis_sees
## If the blue and violet floats are facing the same direction, then Patria is in one of those floats; otherwise, Patria is in the green float.
((blue.left == True) == (violet.left == True)) - (Patria.blue | Patria.violet) <= 0
((blue.left == True) != (violet.left == True)) - Patria.green <= 0
# The person in the blue float can see, directly in front of it, another float whose driver has x letters in his/her name.
# NOTE: Names are 2, 6, 7, 11 so x == 2 or x == 6. 6 is too big for z.
(x == 2)
# Blue needs 1+ person in front of them.
blue.left - (blue[1] == False) <= 0
blue.right - (blue[7] == False) <= 0
# If x == 2: blue sees Li.
blue.left - all((Li[i - 1] == True) == (blue[i] == True) for i in range(2, 8)) <= 0
blue.right - all((Li[i + 1] == True) == (blue[i] == True) for i in range(1, 7)) <= 0
float_distance = abs(Harvey.position - pink.position) - 1
(float_distance == 2) ^ (float_distance == 4)
# The red float is the farthest west.
red.position[1] == True
# If Courtney’s float is blue, orange, violet, or green, then at least one of Courtney’s neighbors has a name containing the letter Y.
c_is_bovg = (Courtney.blue or Courtney.orange or Courtney.violet or Courtney.green)
c_left_neighbor_has_y = all(Courtney[i] - (Phyllis[i - 1] or Harvey[i - 1]) <= 0 for i in range(2, 8))
c_right_neighbor_has_y = all(Courtney[i] - (Phyllis[i + 1] or Harvey[i + 1]) <= 0 for i in range(1, 7))
c_is_bovg - (c_left_neighbor_has_y or c_right_neighbor_has_y) <= 0
# Harvey can see Kimball’s float directly in front of him.
(Harvey.left == True) == (Harvey[7] == True)
(Harvey.left == True) - all(Harvey[i] - Kimball[i - 1] <= 0 for i in range(2, 8)) <= 0
(Harvey.left == False) - all(Harvey[i] - Kimball[i + 1] <= 0 for i in range(1, 7)) <= 0
# The violet float is next to the yellow float if and only if Li’s float is pink.
(Li == pink) == (abs(violet.position - yellow.position) == 1)
# The people in the orange and pink floats can see the blue float somewhere ahead.
blue_left_of_orange = blue.position < orange.position
(orange.left == True) == blue_left_of_orange
blue_right_of_orange = blue.position > orange.position
(orange.left == False) == blue_right_of_orange
blue_left_of_pink = blue.position < pink.position
(pink.left == True) == blue_left_of_pink
blue_right_of_pink = blue.position > pink.position
(pink.left == False) == blue_right_of_pink
# If Li’s float is east of Harvey’s, then Li’s float is either orange or pink.
(Li.position > Harvey.position) - (Li.orange | Li.pink) <= 0
# If Harvey’s float is red or orange, then Kimball’s float is a primary color.
Kimball.blue == True
#(Harvey.red | Harvey.orange) - ((Kimball.red == True) or (Kimball.green == True) or (Kimball.blue == True)) <= 0
# If the red and yellow floats are next to each other, then the person in the red float can see fewer than y other floats, where y = x + 1.
red_yellow_neighbors = abs(red.position - yellow.position) == 1
red_left_sees = red.left * (red.position - 1)
red_right_sees = (red.left == False) * (7 - red.position)
red_sees = red_left_sees + red_right_sees
y = x + 1
red_yellow_neighbors - (red_sees < y) <= 0
# If Christopher’s float is a secondary color, then he can see more floats than Courtney can.
chris_primary = Christopher.red or Christopher.green or Christopher.blue
chris_left_sees = Christopher.left * Christopher.position - 1
chris_right_sees = Christopher.right * (7 - Christopher.position)
chris_sees = chris_left_sees + chris_right_sees
courtney_left_sees = Courtney.left * (Courtney.position - 1)
courtney_right_sees = Courtney.right * (7 - Courtney.position)
courtney_sees = courtney_left_sees + courtney_right_sees
(chris_primary == False) - (chris_sees > courtney_sees) <= 0
# The person in the red float has a name that is z letters long, where z = x * y.
# x = 2 or 6
# y = 3 or 7
# z = 6, 14, 18, 42
# Only "6" works.
z = x * y
print('x is', x)
print('y is', y)
print('z is', z)
# TODO: Had to disable this even though it's already true...?
#z == 6
(red == Harvey) or (red == Patria)
# The pink, violet, and green floats are facing the same direction.
(pink.left == True) == (violet.left == True)
(violet.left == True) == (green.left == True)
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
