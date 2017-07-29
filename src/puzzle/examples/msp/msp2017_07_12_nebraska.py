from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Nebraska', SOURCE)


SOURCE = """
position in range(1, 25 + 1)
name in {
  Andrea,
  Bob,
  Christine,
  Diane,
  Eleanor,
  Felicia,
  Greg,
  Hattie,
  Ignatio,
  Joshua,
  Kaitlyn,
  Lawrence,
  Maddie,
  Nelson,
  Olaf,
  Patrick,
  Quentin,
  Rachel,
  Sarah,
  Tim,
  Ulysses,
  Vanessa,
  Wilma,
  Yolanda,
  Zachary,
}

def between(a, b, c):
  return (b.position > a.position) + (b.position > c.position) == 1

def dist(a, b):
  return abs(a.position - b.position) - 1

def gap(a, n, b):
  return abs(a.position - b.position) == n + 1

# “There are exactly three people between Lawrence and me, not including ourselves.” — Andrea
gap(Lawrence, 3, Andrea)

# “Vanessa is closer to Hattie than to me.” — Bob
dist(Vanessa, Hattie) < dist(Bob, Vanessa)

# “I am next to exactly one of Hattie or Eleanor.” — Christine
gap(Christine, 0, Hattie) or gap(Christine, 0, Eleanor)

# “I am sitting next to at least one of Greg, Andrea, and Patrick.” — Diane
gap(Diane, 0, Greg) | gap(Diane, 0, Andrea) | gap(Diane, 0, Patrick)

# “Both of my neighbors come after me alphabetically.” — Eleanor
gap(Eleanor, 0, Andrea) + gap(Eleanor, 0, Bob) + gap(Eleanor, 0, Christine) + gap(Eleanor, 0, Diane) == 0

# “I am sitting exactly halfway between Maddie and Wilma.” — Felicia
Felicia.position * 2 == Maddie.position + Wilma.position

# “I am sitting at one of the ends of the swing.” — Greg
Greg == 1 or Greg == 25

# “Yolanda is at one of the ends of the swing.” — Hattie
Yolanda == 1 or Yolanda == 25

# “I am sitting between Patrick and Lawrence.” — Ignatio
between(Patrick, Ignatio, Lawrence)

# “There are either four or five people between Greg and me, not including ourselves.” — Joshua
gap(Greg, 4, Joshua) or gap(Greg, 5, Joshua)

# “I am next to at least one person whose name starts with a vowel.” — Kaitlyn
gap(Kaitlyn, 0, Andrea) + gap(Kaitlyn, 0, Eleanor) + gap(Kaitlyn, 0, Ignatio) + gap(Kaitlyn, 0, Olaf) + gap(Kaitlyn, 0, Ulysses) > 0

# “Vanessa is sitting between Christine and myself.” — Lawrence
between(Christine, Vanessa, Lawrence)

# “There are exactly seven people between Kaitlyn and me, not including ourselves.” — Maddie
gap(Kaitlyn, 7, Maddie)

# “There are at least five people between me and each end of the swing.” — Nelson
Nelson.position > 5
Nelson.position < 25 - 5

# “I am next to two of Eleanor, Rachel, or Zachary.” — Olaf
gap(Olaf, 0, Eleanor) + gap(Olaf, 0, Rachel) + gap(Olaf, 0, Zachary) >= 2

# “I am sitting between Lawrence and Maddie.” — Patrick
between(Maddie, Patrick, Lawrence)

# “Both my neighbors have names that are exactly five letters long.” — Quentin
gap(Quentin, 0, Diane) + gap(Quentin, 0, Sarah) + gap(Quentin, 0, Wilma) >= 2

# “I am next to Olaf if and only if I’m also next to Kaitlyn.” — Rachel
gap(Rachel, 0, Olaf) == gap(Rachel, 0, Kaitlyn)

# “I am exactly the same distance from Kaitlyn as from Maddie.” — Sarah
(Kaitlyn.position - Sarah.position) == (Sarah.position - Maddie.position)

# “I am next to Felicia if and only if she is also next to Joshua.” — Tim
gap(Tim, 0, Felicia) == gap(Felicia, 0, Joshua)

# “There is exactly one other person between Kaitlyn and myself.” — Ulysses
gap(Kaitlyn, 1, Ulysses)

# “I am not next to Lawrence, but there are at most seven people between him and me.” — Vanessa
dist(Vanessa, Lawrence) > 0
dist(Vanessa, Lawrence) <= 7

# “I am next to at least one of Bob and Andrea.” — Wilma
gap(Wilma, 0, Bob) | gap(Wilma, 0, Andrea)

# “I am next to Christine.” — Yolanda
gap(Yolanda, 0, Christine)

# “There are exactly three people between Yolanda and me, not including ourselves.” — Zachary
gap(Zachary, 3, Yolanda)
"""

SOLUTION = """
position |      name
       1 |      Greg
       2 |       Bob
       3 |     Wilma
       4 |       Tim
       5 |   Felicia
       6 |    Joshua
       7 |    Maddie
       8 |   Patrick
       9 |     Diane
      10 |   Quentin
      11 |     Sarah
      12 |   Eleanor
      13 |      Olaf
      14 |    Rachel
      15 |   Kaitlyn
      16 |   Ignatio
      17 |   Ulysses
      18 |  Lawrence
      19 |    Nelson
      20 |   Vanessa
      21 |   Zachary
      22 |    Andrea
      23 |    Hattie
      24 | Christine
      25 |   Yolanda
"""
