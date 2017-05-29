from puzzle.puzzlepedia import puzzle


def get(correct):
  if correct:
    return puzzle.Puzzle('A basic puzzle', SOURCE_CORRECT)
  return puzzle.Puzzle('A basic puzzle (initial/wrong)', SOURCE_INITIAL)


SOURCE_INITIAL = """
@ 1 5 2 13 4 12 5 6 2 11
* GABE PRUITT
* SMOKEY II
* TONY GREENE?
* TOM IZZO
* MICHAEL BRADLEY?
* BARACK OBAMA
* CHRISTIAN WEBSTER
* CLEANTHONY EARLY
* GRAYSON ALLEN
* NRG STADIUM?
"""

SOURCE_CORRECT = """
@ 1 5 2 13 4 12 5 6 2 11
* GABE PRUITT
* SMOKEY
* LEE JONES
* TOM IZZO
* MICHAEL BRADLEY
* BARACK OBAMA
* CHRISTIAN WEBSTER
* CLEANTHONY EARLY
* GRAYSON ALLEN
* NRG STADIUM
"""
