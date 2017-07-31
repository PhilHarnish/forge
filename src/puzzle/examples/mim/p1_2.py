from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Puzzle 1.2: True-False Test', SOURCE)


SOURCE = """
name in {Beth1, Beth2, Charles1, Charles2, David1, David2, Frank1, Frank2, Jessica1, Jessica2, Karen1, Karen2, Taylor1, Taylor2}
# Setup: Clubs x4, Diamonds x4, Hearts x3, Spades x3.
suit in {Club, Club, Club, Club, Diamond, Diamond, Diamond, Diamond, Heart, Heart, Heart, Spade, Spade, Spade}

b = [Beth1, Beth2]
c = [Charles1, Charles2]
d = [David1, David2]
f = [Frank1, Frank2]
j = [Jessica1, Jessica2]
k = [Karen1, Karen2]
t = [Taylor1, Taylor2]

def has(person, suit):
  a, b = person
  return a[suit] + b[suit]
  
def hand(person, suit1, suit2):
  a, b = person
  return (a[suit1] and b[suit2]) or (a[suit2] and b[suit1])

(hand(b, club, spade)) or (hand(b, heart, spade))
(hand(c, diamond, heart)) or (has(c, spade) >= 1)
(hand(d, club, spade)) or (has(d, spade) == 1)
(hand(f, club, heart)) or (hand(f, club, spade))
(hand(j, club, spade)) or ((has(j, spade) == 1) and (has(j, diamond) == 0))
(has(k, diamond) == 0) or (has(k, spade) >= 1)
(hand(t, club, heart)) or (has(t, club) == 2 or has(t, diamond) == 2 or has(t, heart) == 2 or has(t, spade) == 2)
"""

SOLUTION = """
    name |    suit
   Beth1 |   Spade
   Beth2 |    Club
Charles1 |   Heart
Charles2 | Diamond
  David1 | Diamond
  David2 |   Spade
  Frank1 |    Club
  Frank2 |   Heart
Jessica1 |   Heart
Jessica2 |   Spade
  Karen1 |    Club
  Karen2 |    Club
 Taylor1 | Diamond
 Taylor2 | Diamond
"""
