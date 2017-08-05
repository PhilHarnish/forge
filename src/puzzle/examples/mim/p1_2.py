from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Puzzle 1.2: True-False Test', SOURCE)


SOURCE = """
(name, hand) in ({Beth, Charles, David, Frank, Jessica, Karen, Taylor}, {1, 2})
suit in {Club*4, Diamond*4, Heart*3, Spade*3}

def has(person, suit):
  a, b = person
  return a[suit] + b[suit]
  
def hand(person, suit1, suit2):
  a, b = person
  return (a[suit1] and b[suit2]) or (a[suit2] and b[suit1])

(hand(name.Beth, club, spade)) or (hand(name.Beth, heart, spade))
(hand(name.Charles, diamond, heart)) or (has(name.Charles, spade) >= 1)
(hand(name.David, club, spade)) or (has(name.David, spade) == 1)
(hand(name.Frank, club, heart)) or (hand(name.Frank, club, spade))
(hand(name.Jessica, club, spade)) or (
    (has(name.Jessica, spade) == 1) and (has(name.Jessica, diamond) == 0))
(has(name.Karen, diamond) == 0) or (has(name.Karen, spade) >= 1)
(hand(name.Taylor, club, heart)) or (
    has(name.Taylor, club) == 2 or
    has(name.Taylor, diamond) == 2 or
    has(name.Taylor, heart) == 2 or
    has(name.Taylor, spade) == 2
)
"""

SOLUTION = """
name_hand |    suit
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
