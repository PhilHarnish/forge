from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Puzzle 3.2: Uncommon Knowledge', SOURCE)


SOURCE = """
import collections
import itertools

with init:
  all_players = 'BCDFJKT'
  all_matches = []
  # dict mapping player_name to list of (match_name, score_condition) matches.
  player_matches = collections.defaultdict(list)
  for a, b in itertools.combinations(all_players, 2):
    name = '%sv%s' % (a, b)
    all_matches.append(name)
    player_matches[a].append((name, 'win'))
    player_matches[b].append((name, 'lose'))

# Dimensions.
match in list(all_matches)
result in {win, lose}
game in {chess, shogi, xiangqi}

# Setup.
# Each player played 2 of each type of game.
for matches in player_matches.values():
  sum(chess[m] for m, first in matches) == 2
  sum(shogi[m] for m, first in matches) == 2
  sum(xiangqi[m] for m, first in matches) == 2

def score(p):
  return sum(match[m].result[score_condition] for m, score_condition in player_matches[p])

def record(p, game):
  return sum(match[m].game[game] and match[m].result[score_condition] for m, score_condition in player_matches[p])

#1: T>D @ chess, F>C @ shogi, J>B @ xiangqi
chess.DvT == lose
shogi.CvF == lose
xiangqi.BvJ == lose

#2: K>B @ chess, F>D @ shogi, T>C @ xiangqi
chess.BvK == lose
shogi.DvF == lose
xiangqi.CvT == lose

#3: C>B @ shogi, T>K @ xiangqi
shogi.BvC == lose
xiangqi.KvT == lose

#4: There was a chess game between two undefeated players.
# HACK: With a little bit of work it is easy to determine this is FvT.
match.FvT == chess
# Undefeated until last round implies they won n-1 rounds.
score('F') >= 5
score('T') >= 5

#5: Only one player lost both chess games.
sum(record(p, chess) == 0 for p in all_players) == 1

#6: Jessica's shogi record == Karen's xiangqi record & vice-versa.
record('J', shogi) == record('K', xiangqi)
record('K', shogi) == record('J', xiangqi)

#7: Two players tied for last with 1:5.
sum(score(p) == 1 for p in all_players) == 2

#8a: The winner's...
sum(score(p) == 6 for p in all_players) == 1
#8b: ...shogi opponents had a better shogi record than the runner up.
# At this point Frank and Taylor are always in last round.
# Frank plays C & D, Taylor plays B & J.
if record('C', shogi) + record('D', shogi) > record('B', shogi) + record('J', shogi):
  score('F') == 6
else:
  score('T') == 6

print('Scores:')
print('Beth', score('B'))
print('Charles', score('C'))
print('David', score('D'))
print('Frank', score('F'))
print('Jessica', score('J'))
print('Karen', score('K'))
print('Taylor', score('T'))
"""


SOLUTION = """
match | result |    game
  BvC |   lose |   shogi
  BvD |    win |   chess
  BvF |   lose | xiangqi
  BvJ |   lose | xiangqi
  BvK |   lose |   chess
  BvT |   lose |   shogi
  CvD |   lose | xiangqi
  CvF |   lose |   shogi
  CvJ |   lose |   chess
  CvK |    win |   chess
  CvT |   lose | xiangqi
  DvF |   lose |   shogi
  DvJ |   lose | xiangqi
  DvK |   lose |   shogi
  DvT |   lose |   chess
  FvJ |    win |   chess
  FvK |    win | xiangqi
  FvT |    win |   chess
  JvK |   lose |   shogi
  JvT |   lose |   shogi
  KvT |   lose | xiangqi
"""
