import Numberjack

Andrea = Numberjack.Variable(25, 'Andrea')
Bob = Numberjack.Variable(25, 'Bob')
Christine = Numberjack.Variable(25, 'Christine')
Diane = Numberjack.Variable(25, 'Diane')
Eleanor = Numberjack.Variable(25, 'Eleanor')
Felicia = Numberjack.Variable(25, 'Felicia')
Greg = Numberjack.Variable(25, 'Greg')
Hattie = Numberjack.Variable(25, 'Hattie')
Ignatio = Numberjack.Variable(25, 'Ignatio')
Joshua = Numberjack.Variable(25, 'Joshua')
Kaitlyn = Numberjack.Variable(25, 'Kaitlyn')
Lawrence = Numberjack.Variable(25, 'Lawrence')
Maddie = Numberjack.Variable(25, 'Maddie')
Nelson = Numberjack.Variable(25, 'Nelson')
Olaf = Numberjack.Variable(25, 'Olaf')
Patrick = Numberjack.Variable(25, 'Patrick')
Quentin = Numberjack.Variable(25, 'Quentin')
Rachel = Numberjack.Variable(25, 'Rachel')
Sarah = Numberjack.Variable(25, 'Sarah')
Tim = Numberjack.Variable(25, 'Tim')
Ulysses = Numberjack.Variable(25, 'Ulysses')
Vanessa = Numberjack.Variable(25, 'Vanessa')
Wilma = Numberjack.Variable(25, 'Wilma')
Yolanda = Numberjack.Variable(25, 'Yolanda')
Zachary = Numberjack.Variable(25, 'Zachary')

names = {
  'Andrea': Andrea,
  'Bob': Bob,
  'Christine': Christine,
  'Diane': Diane,
  'Eleanor': Eleanor,
  'Felicia': Felicia,
  'Greg': Greg,
  'Hattie': Hattie,
  'Ignatio': Ignatio,
  'Joshua': Joshua,
  'Kaitlyn': Kaitlyn,
  'Lawrence': Lawrence,
  'Maddie': Maddie,
  'Nelson': Nelson,
  'Olaf': Olaf,
  'Patrick': Patrick,
  'Quentin': Quentin,
  'Rachel': Rachel,
  'Sarah': Sarah,
  'Tim': Tim,
  'Ulysses': Ulysses,
  'Vanessa': Vanessa,
  'Wilma': Wilma,
  'Yolanda': Yolanda,
  'Zachary': Zachary,
}


model = Numberjack.Model(
    Numberjack.AllDiff(names.values())
)

def gap(a, b, n=None):
  if n is not None:
    return Numberjack.Abs(a - b) == n + 1
  return Numberjack.Abs(a - b) - 1

def between(a, b, c):
  return (b > a) + (b > c) == 1

# “There are exactly three people between Lawrence and me, not including ourselves.” — Andrea
model.add(gap(Andrea, Lawrence, 3))

# “Vanessa is closer to Hattie than to me.” — Bob
model.add(gap(Vanessa, Hattie) < gap(Bob, Vanessa))

# “I am next to exactly one of Hattie or Eleanor.” — Christine
model.add(gap(Christine, Hattie, 0) + gap(Christine, Eleanor, 0) == 1)

# “I am sitting next to at least one of Greg, Andrea, and Patrick.” — Diane
model.add(gap(Diane, Greg, 0) + gap(Diane, Andrea, 0) + gap(Diane, Patrick, 0) >= 1)

# “Both of my neighbors come after me alphabetically.” — Eleanor
model.add(gap(Eleanor, Andrea, 0) + gap(Eleanor, Bob, 0) + gap(Eleanor, Christine, 0) + gap(Eleanor, Diane, 0) == 0)

# “I am sitting exactly halfway between Maddie and Wilma.” — Felicia
model.add(Felicia * 2 == Maddie + Wilma)

# “I am sitting at one of the ends of the swing.” — Greg
model.add((Greg == 0) | (Greg == 24))

# “Yolanda is at one of the ends of the swing.” — Hattie
model.add((Yolanda == 0) | (Yolanda == 24))

# “I am sitting between Patrick and Lawrence.” — Ignatio
model.add(between(Patrick, Ignatio, Lawrence))

# “There are either four or five people between Greg and me, not including ourselves.” — Joshua
model.add(gap(Greg, Joshua, 4) | gap(Greg, Joshua, 5))

# “I am next to at least one person whose name starts with a vowel.” — Kaitlyn
model.add(gap(Kaitlyn, Andrea, 0) | gap(Kaitlyn, Eleanor, 0) | gap(Kaitlyn, Ignatio, 0) | gap(Kaitlyn, Olaf, 0) | gap(Kaitlyn, Ulysses, 0))

# “Vanessa is sitting between Christine and myself.” — Lawrence
model.add(between(Christine, Vanessa, Lawrence))

# “There are exactly seven people between Kaitlyn and me, not including ourselves.” — Maddie
model.add(gap(Kaitlyn, Maddie, 7))

# “There are at least five people between me and each end of the swing.” — Nelson
model.add(Nelson > 0 + 5)
model.add(Nelson < 24 - 5)

# “I am next to two of Eleanor, Rachel, or Zachary.” — Olaf
model.add(gap(Olaf, Eleanor, 0) + gap(Olaf, Rachel, 0) + gap(Olaf, Zachary, 0) >= 2)

# “I am sitting between Lawrence and Maddie.” — Patrick
model.add(between(Maddie, Patrick, Lawrence))

# “Both my neighbors have names that are exactly five letters long.” — Quentin
model.add(gap(Quentin, Diane, 0) + gap(Quentin, Sarah, 0) + gap(Quentin, Wilma, 0) >= 2)

# “I am next to Olaf if and only if I’m also next to Kaitlyn.” — Rachel
model.add(gap(Rachel, Olaf, 0) == gap(Rachel, Kaitlyn, 0))

# “I am exactly the same distance from Kaitlyn as from Maddie.” — Sarah
model.add((Kaitlyn - Sarah) == (Sarah - Maddie))

# “I am next to Felicia if and only if she is also next to Joshua.” — Tim
model.add(gap(Tim, Felicia, 0) == gap(Felicia, Joshua, 0))

# “There is exactly one other person between Kaitlyn and myself.” — Ulysses
model.add(gap(Ulysses, Kaitlyn, 1))

# “I am not next to Lawrence, but there are at most seven people between him and me.” — Vanessa
model.add(gap(Vanessa, Lawrence) > 0)
model.add(gap(Vanessa, Lawrence) <= 7)

# “I am next to at least one of Bob and Andrea.” — Wilma
model.add(gap(Wilma, Bob, 0) + gap(Wilma, Andrea, 0) >= 1)

# “I am next to Christine.” — Yolanda
model.add(gap(Yolanda, Christine, 0))

# “There are exactly three people between Yolanda and me, not including ourselves.” — Zachary
model.add(gap(Zachary, Yolanda, 3))


solver = model.load('Mistral')
solver.solve()

print("is_sat", solver.is_sat())
print("is_unsat", solver.is_unsat())

def print_solutions():
  solutions = []
  for name, variable in names.items():
    value = variable.get_value()
    solutions.append((value, name))
    if value == 12:
      print(name)
  for results in sorted(solutions, key=lambda i: i[0]):
    print('%3s: %s' % results)

print_solutions()
print("is_sat", solver.is_sat())
print("is_unsat", solver.is_unsat())

if solver.getNextSolution():
  print('another solution?')
  print_solutions()
  x = 2
  while solver.getNextSolution():
    x += 1
    print(x)
    if Lawrence.get_value() == 12:
      print('found Lawrence == 12')
      print_solutions()
else:
  print('no other solution')
