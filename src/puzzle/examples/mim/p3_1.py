from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Puzzle 3.1: Movie Poll', SOURCE)


SOURCE = """
name in {Beth, Charles, David, Frank, Jessica, Karen, Taylor}
movie in {M4a*4, M4b*4, M3a*3, M2a*2, M2b*2, M1a, M1b, M1c, M1d, M1e, M1f}
unique_movies = [M4a, M4b, M3a, M2a, M2b, M1a, M1b, M1c, M1d, M1e, M1f]
solo_movies = [M1a, M1b, M1c, M1d, M1e, M1f]
#1: Setup.
# Each person listed 3 movies.
for n in name:
  sum(n[m] for m in unique_movies) == 3

#2: <Defines score algorithm>
def score(n):
  return sum(n[m] for m in movie) - 3

#3a: Very few score ties. Two have "2".
sum(score(n) == 2 for n in name) == 2

#3b: Evens (8) never tie.
sum(score(n) == 3 for n in name) == 1
sum(score(n) == 5 for n in name) == 1
sum(score(n) == 7 for n in name) == 2
sum(score(n) == 8 for n in name) == 1

#4: Jessica & Taylor shared; Charles & Frank too.
def shared(a, b):
  return sum(a[m] and b[m] for m in unique_movies)

shared(Jessica, Taylor) == 1
shared(Charles, Frank) == 1

#5: Frank and Karen had 1 solo movie each.
def solo(n):
  return sum(n[m] for m in solo_movies)

solo(Frank) == 1
solo(Karen) == 1

#6a: Taylor listed 2 solo movies...
solo(Taylor) == 2

#6b: ...and scored 4 points less than David
score(Taylor) + 4 == score(David)

#7:
score(Karen) > 2

#8:
solo(Beth) >= 1

print('Beth', score(Beth))
print('Charles', score(Charles))
print('David', score(David))
print('Frank', score(Frank))
print('Jessica', score(Jessica))
print('Karen', score(Karen))
print('Taylor', score(Taylor))
"""

SOLUTION = """
   name |         movie
   Beth | M3a, M1a, M1b
Charles | M4a, M4b, M2a
  David | M4a, M4b, M2b
  Frank | M2a, M2b, M1d
Jessica | M4a, M4b, M3a
  Karen | M4a, M3a, M1e
 Taylor | M4b, M1c, M1f
"""
