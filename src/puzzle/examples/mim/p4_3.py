from puzzle.puzzlepedia import puzzle


def get():
  return puzzle.Puzzle('Puzzle 4.3: ', SOURCE)


SOURCE = """
name in {Beth, Charles, David, Frank, Jessica, Karen, Taylor}
crime in {innocent, first, last}

# Note: ckt_first2 ends up only ever being false.
ckt_first2 is bool
if Charles == first or Karen == first or Taylor == first: ckt_first2 == True
# Note: bfk_last2 ends up only ever being false.
bfk_last2 is bool
if Beth == last or Frank == last or Karen == last: bfk_last2 == True
# By contrast, this is essential to solving.
david_before_charles is bool
if David == last: david_before_charles == False
if Charles == last: david_before_charles == True
if David == first: david_before_charles == True
if Charles == first: david_before_charles == False

#1: Two criminals.
sum(n.first for n in name) == 1
sum(n.last for n in name) == 1

#2: n/a.

#3: First to enter is guilty.

#4: Last to leave is guilty.

#5: n/a.

#6:
David != first
Frank != first

#7:
Charles != last
Jessica != last

#8:
if Beth.innocent:
  (Jessica == first) | (David == last)

#9:
if Charles.innocent:
  Charles != first
  Karen != first
  Taylor != first
  ckt_first2 == False
  Beth != last
  Frank != last
  Karen != last
  bfk_last2 == False

#10:
if David.innocent:
  David != last
  Charles != first
  Karen != first
  Taylor != first
  ckt_first2 == False

#11:
if Frank.innocent:
  (David != last) | (Jessica != first)
  if Jessica == first:
    david_before_charles == True  

#12:
if Jessica.innocent:
  david_before_charles == False
  David != last
  Beth != last
  Frank != last
  Karen != last
  bfk_last2 == False

#13:
if Karen.innocent:
  (Charles != last) | (Jessica != first)
  if Jessica == first:
    david_before_charles == False 

#14:
if Taylor.innocent:
  bfk_last2 == True

print('david_before_charles', david_before_charles)
"""


SOLUTION = """
   name |    crime
   Beth |    first
Charles | innocent
  David | innocent
  Frank | innocent
Jessica | innocent
  Karen | innocent
 Taylor |     last
"""
