from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Puzzle 3.2: Uncommon Knowledge', SOURCE)


SOURCE = """
import itertools
name in {Beth, Charles, David, Frank, Jessica, Karen, Taylor}
item in {cards, cars, comics, ducks, perfume, spoons, jugs}
language in {Dutch, French, Japanese, Portuguese, Russian, Spanish, Tagalog}

def mix(a, b):
  return sum(x[y] for x, y in itertools.product(a, b)) == len(a)

#1:
mix([cards, cars, jugs], [French, Japanese, Tagalog])

#2:
mix([Charles, Frank, Karen], [Dutch, French, Russian])

#3:
mix([David, Jessica, Taylor], [cards, spoons, jugs])

#4:
Beth.Spanish or Beth.ducks

#5:
Charles.French or Charles.comics

#6:
David.Japanese or David.cards

#7:
Jessica.Spanish or Jessica.cards

#8:
Karen.Russian or Karen.comics

#9:
Taylor.Tagalog or Taylor.jugs

#10
Frank != Russian
Frank != cars

#11
if Charles == cars:
  David != Japanese
"""


SOLUTION = """
   name |    item |   language
   Beth |   ducks | Portuguese
Charles |    cars |     French
  David |   cards |    Tagalog
  Frank |  comics |      Dutch
Jessica |  spoons |    Spanish
  Karen | perfume |    Russian
 Taylor |    jugs |   Japanese
"""
