from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Puzzle 4.4: Garden Plots', SOURCE)


SOURCE = """
import itertools
plot in {A, B, C, D, E, F, G, H, I, J, K, L, M, N}
vegetable in {
  asparagus, broccoli, cabbage, carrots, cucumbers, green_beans, lettuce,
  peas, peppers, potatoes, radishes, squash, tomatoes, turnips,
}
name in {Beth, Charles, David, Frank, Jessica, Karen, Taylor}

neighbor_map = {
  A: [B, D, E],
  B: [A, C, E, F],
  C: [B, F],
  D: [A, E, G, J],
  E: [A, B, D, F, G, H],
  F: [B, C, E, H, I],
  G: [D, E, H, J, K, L],
  H: [E, F, G, L, M, I],
  I: [F, H, M, N],
  J: [D, G, K],
  K: [J, G, L],
  L: [G, H, K, M, N],
  M: [H, I, L, N],
  N: [I, L, M],
}
valid_pairs = []
pairs_with_neighbor_pairs = []

SUSPECTED_ASPARAGUS = H

with init:
  valid_pairs_seen = set()
  for center, neighbors in neighbor_map.items():
    for neighbor in neighbors:
      key = ''.join(sorted([str(center), str(neighbor)]))
      if key in valid_pairs_seen:
        continue
      valid_pairs_seen.add(key)
      valid_pairs.append([center, neighbor])
  for (pa, pa_neighbors), (pb, pb_neighbors) in itertools.combinations(neighbor_map.items(), 2):
    if pb.dimension_constraints() == SUSPECTED_ASPARAGUS.dimension_constraints():
      pa, pb = pb, pa
    if pa.dimension_constraints() != SUSPECTED_ASPARAGUS.dimension_constraints():
      continue
    shared_neighbors = set(pa_neighbors).intersection(set(pb_neighbors))
    for n1, n2 in itertools.combinations(shared_neighbors, 2):
      pairs_with_neighbor_pairs.append(((pa, pb), (n1, n2)))

def pair_border_plots(v1, v2, n1, n2):
  return sum([
    (pa[v1] and pb[v2] and (na[n1] or na[n2]) and (nb[n1] or nb[n2]))
    for (pa, pb), (na, nb) in pairs_with_neighbor_pairs
  ]) == 1

def pair_border_names(v1, v2, n1, n2):
  return sum(nx[v1] or nx[v2] or nx[n1] or nx[n2] for nx in name) == 4

def pair_border(v1, v2, n1, n2):
  return pair_border_names(v1, v2, n1, n2) and pair_border_plots(v1, v2, n1, n2)


#1: 2 plots pp.
# NB: No longer needed. Plots have been solved with only Charles and Frank free.
#for nx in [Charles, Frank]:
#  sum(nx[p1] and nx[p2] for p1, p2 in valid_pairs) == 1

#2, #3, #4: Establish valid plot->name assignments.
# There are only two valid solutions:
# plot |    name  plot |    name
#    A | Charles     A |   Frank
(A == Charles and E == Charles) or (A == Frank and E == Frank)
#    B |   Karen     B |   Karen
B == Karen
#    C |   Karen     C |   Karen
C == Karen
#    D |  Taylor     D |  Taylor
D == Taylor
#    E | Charles     E |   Frank
# NB: A and E constrained at same time above.
#    F | Jessica     F | Jessica
F == Jessica
#    G |  Taylor     G |  Taylor
G == Taylor
#    H |   Frank     H | Charles
(H == Frank and M == Frank) or (H == Charles and M == Charles)
#    I | Jessica     I | Jessica
I == Jessica
#    J |   David     J |   David
J == David
#    K |   David     K |   David
K == David
#    L |    Beth     L |    Beth
L == Beth
#    M |   Frank     M | Charles
# NB: H and M constrained at same time above.
#    N |    Beth     N |    Beth
N == Beth

#5: Corner plots.
for px in [A, C, J, N]:
  sum(px[vx] for vx in [broccoli, carrots, green_beans, radishes]) == 1

#6:
pair_border(asparagus, lettuce, squash, tomatoes)

#7:
pair_border(asparagus, peas, cucumbers, turnips)

#8:
pair_border(asparagus, squash, tomatoes, turnips)

#9:
pair_border(asparagus, turnips, cucumbers, squash)

#10:
for center, neighbors in neighbor_map.items():
  if center == peppers:
    sum(nx[green_beans] + nx[potatoes] for nx in neighbors) == 2
    all(nx != Frank for nx in neighbors)

#11:
# Jessica is in I and F.
((sum(nx[potatoes] + nx[radishes] for nx in neighbor_map[I]) == 2) or
 (sum(nx[potatoes] + nx[radishes] for nx in neighbor_map[F]) == 2))

#12:
# David is in J and K.
David != broccoli
David != lettuce
sum(nx[squash] + nx[tomatoes] for nx in [D, J, L]) == 0
"""


SOLUTION = """
plot |   vegetable |    name
   A |    broccoli |   Frank
   B |     lettuce |   Karen
   C |    radishes |   Karen
   D |     cabbage |  Taylor
   E |      squash |   Frank
   F |    tomatoes | Jessica
   G |     turnips |  Taylor
   H |   asparagus | Charles
   I |    potatoes | Jessica
   J |     carrots |   David
   K |        peas |   David
   L |   cucumbers |    Beth
   M |     peppers | Charles
   N | green_beans |    Beth
"""
