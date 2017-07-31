from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Puzzle 1.1: Meet the Guests', SOURCE)


SOURCE = """
position in range(8 + 1)
name in {Beth, Charles, David, Frank, Jessica, Karen, Taylor, Gordon, Nina}
state in {CA, FL, KY, MT, NY, TX, WI, XX, ZZ}
handed in {left, right}

def dist(a, b):
  return abs(a.position - b.position) - 1

def near(a, b):
  return abs(a.position - b.position) == 1

# 0:
Gordon[0] == True
Gordon == right
Gordon == XX
# NB: 5 is a different seat in the book.
Nina[5] == True
Nina == right
Nina == ZZ

# 1a: two left handed people sitting in the corners.
left[1] == True
left[6] == True
all(right[i] for i in [0, 2, 3, 4, 5, 7, 8])

# 2: Montana is next to Florida and Wisconson.
near(MT, FL)
near(MT, WI)
# ...and are both right handed.
FL == right
WI == right

# 3a: Taylor is not from MT
Taylor != MT
Taylor != CA
# 3b: And everyone is right handed.
Taylor == Right
MT == right
CA == right

# 4a: Frank and Jessica are right handed.
Frank == right
Jessica == right
# 4b: ...and sit on opposite sides of the table.
if Frank.position < 5:
  Jessica.position > 5
else:
  Jessica.position < 5

# 5: NY is right handed
NY == right

# 6a: Charles and FL are near the left-handed guests
Charles != FL
Charles[2] or Charles[7]
FL[2] or FL[7]

# 7: Frank and CA are next to Montagues.
Frank != CA
Frank[1] or Frank[4] or Frank[6] or Frank[8]
CA[1] or CA[4] or CA[6] or CA[8]

# 8a: Beth is on same side as TX
Beth != TX
if Beth.position < 5:
  TX.position < 5
else:
  TX.position > 5

# 8b: ...who is not Karen
Karen != TX
"""

SOLUTION = """
position |    name | state | handed
       0 |  Gordon |    XX |  right
       1 |   David |    TX |   left
       2 |  Taylor |    FL |  right
       3 |    Beth |    MT |  right
       4 |   Frank |    WI |  right
       5 |    Nina |    ZZ |  right
       6 |   Karen |    KY |   left
       7 | Charles |    NY |  right
       8 | Jessica |    CA |  right
"""
