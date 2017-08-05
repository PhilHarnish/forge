from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Puzzle 1.2: True-False Test', SOURCE)


SOURCE = """
name in {Beth, Charles, David, Frank, Jessica, Karen, Taylor, empty*8}
(room, floor) in ({A, B, C, D, E}, {1, 2, 3})

def on_floor(n, floor_number):
  return sum(n[f] for f in floor[floor_number]) == 1

def floor_n(n):
  return sum(n[f] for f in floor[1]) + 2*sum(n[f] for f in floor[2]) + 3*sum(n[f] for f in floor[3])

#1: 8 of the 15 rooms are empty.
# (Implicit with "name" definition above with 8 "empty" names.)

#2: 2+ people per floor.
for f in [floor[1], floor[2], floor[3]]:
  sum(not r.empty for r in f) >= 2

#3: Some people share closets with guests, sorta.
closet_neighbors = [Beth, David, Jessica, Taylor]
# NB: No closet linking 3D/E3.
closet_neighbor_map = {
  A1: B1,
  A2: B2,
  A3: B3,
}
closet_neighbor_banned_rooms = [
  C1, C2, C3,
  D1, D2, D3,
  E1, E2, E3,
]
# Ensure, for example, that if Beth is in "A1" then "B1" is not empty.
for n in closet_neighbors:
  for a, b in closet_neighbor_map.items():
    if n[a]: not b.empty
    if n[b]: not a.empty
  for a in closet_neighbor_banned_rooms:
    n[a] == False

#4a: Karen is next to someone with a closet crawlspace.
# Map of rooms-with-crawlspace-closets -> neighbors.
closet_crawlspaces = {
  C1: [A1, B1],
  C2: [A2, B2],
  C3: [A3, B3],
  E3: [D3],
}
karen_eligible = [A1, B1, A2, B2, A3, B3, D3]
# Karen needs to be in one of those closet neighbor rooms.
sum(Karen[n] for n in karen_eligible) == 1
# And the candidate room will need to be occupied.
for candidate, neighbors in closet_crawlspaces.items():
  if sum(Karen[n] for n in neighbors): not candidate.empty

#4b: Two guests have closets near crawl spaces.
sum(not c.empty for c in closet_crawlspaces) == 2

#5: Beth and Jessica are on separate floors.
floor_n(Beth) != floor_n(Jessica)

#6:
def floor_addr(n):
  return (
      1*n.D1 + 2*n.B1 + 3*n.C1 + 4*n.E1 +
      5*n.E2 + 6*n.C2 + 7*n.B2 + 8*n.D2 + 9*n.A2 +
      10*n.A3 + 11*n.D3 + 12*n.B3 + 13*n.C3 + 14*n.E3
  )

# For some reason the "abs(...) - 1" expression does not work!
def floor_distance(a, b):
  if floor_addr(a) > floor_addr(b):
    result = floor_addr(a) - floor_addr(b)
  else:
    result = floor_addr(b) - floor_addr(a)
  return result - 1

floor_distance(Beth, Charles) * 2 == floor_distance(Jessica, Karen)
floor_distance(Beth, Charles) > 0

#7: David is one floor higher than Frank.
floor_n(David) == floor_n(Frank) + 1

#8
D1.empty + D2.empty + D3.empty < 3
"""


SOLUTION = """
   name |                     room_floor
   Beth |                             A2
Charles |                             E3
  David |                             B2
  Frank |                             C1
Jessica |                             B1
  Karen |                             D3
 Taylor |                             A1
  empty | A3, B3, C2, C3, D1, D2, E1, E2
"""
