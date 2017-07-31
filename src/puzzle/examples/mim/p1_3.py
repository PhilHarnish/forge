from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Puzzle 1.3: The Missing Painting', SOURCE)


SOURCE = """
name in {Beth, Charles, David, Frank, Jessica, Karen, Taylor}
job in {attorny, banker, composer, decorator, entrepreneur, filmmaker, gerontologist}
start in {boathouse, cottage, garden, lighthouse, mansion, pond, windmill}
status in {crime, innocent}

# Setup: only one crime was committed.
sum([n.crime for n in name]) == 1

#2
boathouse.crime or cottage.crime or lighthouse.crime or windmill.crime

#4
if entrepreneur.innocent:
  not mansion.crime

#5
not gerontologist.crime

#6
Karen == decorator

#7
entrepreneur == cottage or entrepreneur == mansion or entrepreneur == pond
filmmaker == cottage or filmmaker == mansion or filmmaker == pond
gerontologist == cottage or gerontologist == mansion or gerontologist == pond

#8
if charles.crime:
  not cottage.crime

#9
if beth.innocent:
  beth == banker
  beth == windmill

#10
if charles.innocent:
  charles == gerontologist
  not charles.mansion
  not charles.pond

#11
if david.innocent:
  not boathouse.crime

#12
if frank.innocent:
  frank != entrepreneur
  entrepreneur != mansion

#13
if jessica.innocent:
  mansion.innocent
  pond.innocent
  jessica != mansion
  jessica != pond

#14
if karen.innocent:
  karen == lighthouse
  boathouse == innocent
  mansion == innocent

#15
if taylor.innocent:
  taylor == attorny
  taylor == garden
  if windmill.crime:
    jessica.crime
"""

SOLUTION = """
   name |           job |      start |   status
   Beth |        banker |   windmill | innocent
Charles | gerontologist |    cottage | innocent
  David |  entrepreneur |       pond | innocent
  Frank |     filmmaker |    mansion | innocent
Jessica |      composer |  boathouse | innocent
  Karen |     decorator | lighthouse |    crime
 Taylor |       attorny |     garden | innocent
"""
