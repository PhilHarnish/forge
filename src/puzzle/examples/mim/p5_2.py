from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Puzzle 5.2: The Lost Goban', SOURCE)


SOURCE = """
name in {Beth, Charles, David, Frank, Jessica, Karen, Taylor}
city in {Abu_Dhabi, Beijing, Chennai, Manila, Seoul, Singapore, Tokyo}
occupation in {historian, investigator, journalist, knitter, linguist, magician, numismatist}
weeks_ago in {3, 3, 2, 2, 2, 1, 1}
crime in {innocent*6, guilty}

#1: Setup: Occupations, 1 thief.

#2: Setup: Locations.

#3:
{Charles, Frank, Karen} == {linguist, magician, numismatist}
all(Charles[w] == Frank[w] == Karen[w] for w in [1, 2, 3])

#4:
Chennai != knitter

#5:
magician != Beijing
numismatist != Beijing

#6:
{Manila} == {knitter, linguist, magician}
investigator != Seoul
investigator == innocent
all(investigator[w] == guilty[w] for w in [1, 2, 3])

#7:
Beth.weeks_ago > knitter.weeks_ago
Jessica.weeks_ago > historian.weeks_ago

#8:
all(Chennai[w] == Tokyo[w] for w in [1, 2, 3])

#9:
if Beth.innocent:
  Charles == Abu_Dhabi or Charles == Beijing

#10:
if Charles.innocent:
  David == Beijing or David == Chennai

#10:
if David.innocent:
  Frank == Chennai or Frank == Manila

#10:
if Frank.innocent:
  Jessica == Manila or Jessica == Seoul

#10:
if Jessica.innocent:
  Karen == Seoul or Karen == Singapore

#10:
if Karen.innocent:
  Taylor == Singapore or Taylor == Tokyo 

#10:
if Taylor.innocent:
  Beth == Tokyo or Beth == Abu_Dhabi
"""

SOLUTION = """
   name |      city |   occupation | weeks_ago |    crime
   Beth | Abu_Dhabi | investigator |         3 | innocent
Charles |   Beijing |     linguist |         2 | innocent
  David |   Chennai |    historian |         1 | innocent
  Frank |    Manila |     magician |         2 | innocent
Jessica |     Seoul |   journalist |         3 |   guilty
  Karen | Singapore |  numismatist |         2 | innocent
 Taylor |     Tokyo |      knitter |         1 | innocent
"""
