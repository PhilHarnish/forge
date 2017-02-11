from expects import *
from src.origen import seven_segment

_A = """a
###
  #
###
# #
###
"""

with description('parser'):
  with it('parses simple input'):
    letter = seven_segment.parse(_A)
    expect(letter.ascii).to(equal('a'))
    expect(letter.segments).to(equal([2, 7, 3]))
