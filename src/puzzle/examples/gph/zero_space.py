from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Zero Space', SOURCE, hint='crossword')


SOURCE = """
76ers legend nickname
Action paired with "chew bubblegum"
AP test with a document-based question
Apparatus with "Yes", "No", and "Good Bye"
Benjamin
Card game in which players ask questions
Circuit element implementing the ⊕ operator
Dark Souls failure message
Deceptive cannon made of wood
Document with potential victims
Free legal work
Hollis Frampton film
It follows a long trip
It's below B and C?
It's mostly made of methane
Joker, e.g.
Little Boy dropper
Mesh well
Metal group?
"My bad"
Not moving
President attacked in the Gold Spoon Oration
Reverse, as a car
Stark alias
Symbol that indicates inspiration
Vomit
"""

SOLUTIONS = """
DR J
KICK ASS
US HISTORY
OUIJA BOARD
C NOTE
GO FISH
XOR GATE
YOU DIED
QUAKER GUN
HIT LIST
PRO BONO
ZORNS LEMMA
JET LAG
SPACE BAR
NATURAL GAS
WILD CARD
ENOLA GAY
FIT IN
RARE EARTH
MEA CULPA
AT REST
VAN BUREN
BACK UP
IRON MAN
LIGHT BULB
THROW UP
""".strip().split('\n')
