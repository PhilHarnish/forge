from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Puzzle 10.1: Birdwatching', SOURCE)


SOURCE = """
import itertools
import functools

name in {Beth, Charles, David, Frank, Jessica, Karen, Taylor}
place in {Island, Lookout, North, pond, windmill}
bird in {
  black, blue, bunting, dove, duck, gull, heron, humming, ibis, killdeer, lark,
  martin, osprey, owl, pelican, pheasant, tern, warbler, wood
}

@functools.lru_cache()
def n_birds(p):
  return sum(p[b] for b in bird)

@functools.lru_cache()
def saw_bird(b):
  return sum(n[b] for n in name)

model.disable_constraints()
model.disable_inference()
model.solve_with('MiniSat')

# Constraints.
# Each person visited 3 locations.
for n in name:
  sum(n[p] for p in place) == 3
# Each bird appears in only one location.
for b in bird:
  sum(b[p] for p in place) == 1

# Inference.
# if place["North"].bird["gull"]:
#   name["Taylor"].bird["gull"] == name["Taylor"].place["North"] 
for n, p, b in itertools.product(name, place, bird):
  if b[p]: n[b] == n[p]


#1a: Everyone went to different locations.
def hash_locations(n):
  return sum((1<<i) * n[p] for i, p in enumerate(place))

all_diff([hash_locations(n) for n in name])

#2: Visiting a location implies seeing the birds there.

#3: Each location has different number of species.
all_diff([n_birds(p) for p in place])

#4: Someone saw 6 species, another 16. 10, 11, and 13 are not options.
# 10: Gordon.
gordon_birds is range(10, 10)
# 11: Nina.
nina_birds is range(11, 11)
# 13: Nolan.
nolan_birds is range(13, 13)
all_diff([gordon_birds, nina_birds, nolan_birds] + [n_birds(n) for n in name])

#5a:
saw_bird(heron) > saw_bird(blue)
#5b:
saw_bird(osprey) == 3

#6:
for n in {Beth, Charles, David, Frank, Jessica, Karen, Taylor} - {Charles, Jessica}:
  n == pond
Charles != pond
Jessica != pond

#7:
for n in {Beth, Charles, David, Frank, Jessica, Karen, Taylor} - {Beth, Taylor}:
  n == windmill
Beth != windmill
Taylor != windmill

#8:
Beth == killdeer
David == killdeer
Jessica == killdeer

#9a:
for n in {Beth, Charles, David, Frank, Jessica, Karen, Taylor} - {Frank, Karen, Taylor}:
  n == pheasant
  n == North
#9b:
pheasant == North

#10:
Beth == pelican
Jessica == pelican

#11:
any(p.blue and p.gull and p.black and p.tern for p in place)

#12:
any(p.lark and p.heron and p.humming and p.duck for p in place)

#13:
for n in {Beth, Frank, Jessica, Taylor}:
  n == dove
for n in {Charles, David, Karen}:
  n != dove

#14a:
for n in {Beth, Charles, David, Frank, Jessica, Karen, Taylor} - {Beth, Jessica}:
  (n.bunting and n.wood) == False
Beth.bunting and Beth.wood
Jessica.bunting and Jessica.wood
#14b:
for n in {Beth, Charles, David, Frank, Jessica, Karen, Taylor} - {Charles}:
  (n.martin and n.wood) == False
Charles.martin and Charles.wood
#14c:
for n in {Beth, Charles, David, Frank, Jessica, Karen, Taylor} - {Taylor}:
  (n.bunting and n.martin) == False
Taylor.bunting and Taylor.martin

#15a:
sum(Jessica[b] and Karen[b] for b in bird) == 1
#15b:
Jessica == owl
Karen == owl

#16a:
bunting != Lookout

#16b:
all(bunting[p] == warbler[p] for p in place)

#17
all(not (ibis[p] and pelican[p]) for p in place)

#18
n_birds(Island) > n_birds(North)

# DO NOT SUBMIT. Debugging.
def set_place(superset, subset, place):
  return (
      all(x == place for x in subset) and
      all(x != place for x in set(superset) - subset)
  )

#set_place(bird, {osprey, martin}, Lookout)


model.grid()
for n in name:
  print(n, n_birds(n))
"""


SOLUTION = """
   name |                    place |                                                                                                                 bird
   Beth |      Island, North, pond | black, blue, bunting, dove, duck, gull, heron, humming, ibis, killdeer, lark, pelican, pheasant, tern, warbler, wood
Charles | Lookout, North, windmill |                                                                        killdeer, martin, osprey, owl, pheasant, wood
  David |    North, pond, windmill |                                                      duck, heron, humming, ibis, killdeer, lark, owl, pheasant, wood
  Frank |   Island, pond, windmill |                      black, blue, bunting, dove, duck, gull, heron, humming, ibis, lark, owl, pelican, tern, warbler
Jessica |  Island, North, windmill |                              black, blue, bunting, dove, gull, killdeer, owl, pelican, pheasant, tern, warbler, wood
  Karen |  Lookout, pond, windmill |                                                                duck, heron, humming, ibis, lark, martin, osprey, owl
 Taylor |    Island, Lookout, pond |           black, blue, bunting, dove, duck, gull, heron, humming, ibis, lark, martin, osprey, pelican, tern, warbler
"""
