""" Blue in {2,3} Blue
Brown in {4} Brown
Purple in {8} Purple
Yellow in {10} Yellow
Green in {5} Green
Cyan in {1} Cyan
Orange in {6,9} Orange
Black in {9} Black
Magenta in {14} Magenta
Gray #1 in {12} Gray #1
White in {11} White
Red in {13} Red
Gray #2 in {7} Gray #2
"""
import Numberjack

"""On the subject of Roses"""


def _make_roses(*names):
  result = {}
  for name in names:
    result[name] = Numberjack.Variable(1, 14, name)
  return result


_ROSES = _make_roses('Blue', 'Brown', 'Green', 'Purple', 'Black', 'Gray #1',
    'Magenta', 'Cyan', 'Gray #2', 'Orange', 'Yellow', 'Red', 'White', 'Gray #3')

model = Numberjack.Model(
    # A Black rose is surrounded by roses that share a color.
    # (
    #  _ROSES['Gray #1'] > _ROSES['Black'],
    #  _ROSES['Black'] > _ROSES['Gray #2'],
    # ) | (
    #  _ROSES['Gray #2'] > _ROSES['Black'],
    #  _ROSES['Black'] > _ROSES['Gray #1'],
    # ),
    # A Blue rose is no more than two away from a Gray rose. Eg:
    # 1 2 3 4 5 6
    #   x   x  = 2 away?
    (
      Numberjack.Abs(_ROSES['Blue'] - _ROSES['Gray #1']) <= 2 |
                                                            Numberjack.Abs(
                                                                _ROSES['Blue'] -
                                                                _ROSES[
                                                                  'Gray #2'])
      <= 2
    ),

    # A Magenta rose and a Cyan rose are as far apart as possible.
    Numberjack.Abs(_ROSES['Magenta'] - _ROSES['Cyan']) == (len(_ROSES) - 1),

    # All roses in the right half of the row appear only once in the row.
    ## TODO

    # Every color of rose, except one, appears exactly once.
    Numberjack.AllDiff(_ROSES.values()),

    # Four roses lie between two Gray roses.
    #    1 2 3 4 5 6
    #    x         x  = 5 away?
    Numberjack.Abs(_ROSES['Gray #1'] - _ROSES['Gray #2']) == 5,

    # From right to left, these roses appear in this order, but not necessarily
    #    consecutively: Cyan, Green, Orange, Black, Red.
    _ROSES['Cyan'] > _ROSES['Green'],
    _ROSES['Green'] > _ROSES['Orange'],
    _ROSES['Orange'] > _ROSES['Black'],
    _ROSES['Black'] > _ROSES['Red'],

    # The middle roses are Gray...
    (
      (7 <= _ROSES['Gray #1'] & _ROSES['Gray #1'] <= 8) |
      (7 <= _ROSES['Gray #2'] & _ROSES['Gray #2'] <= 8)
    ),
    #     ...and Purple.
    7 <= _ROSES['Purple'],
    _ROSES['Purple'] <= 8,

    # The rose in the middle of the left half of the row is Brown.
    _ROSES['Brown'] == 4,

    # The sequence Green, Yellow, White appears somewhere in the row of roses.
    _ROSES['Yellow'] - _ROSES['Green'] == 1,
    _ROSES['White'] - _ROSES['Yellow'] == 1,

    # There are an even number of roses.
    #   ???
)

solver = model.load('Mistral')
solver.solve()

for rose, value in sorted(_ROSES.items(), key=lambda x: x[1].get_value()):
  print(value, rose)
print('Nodes:', solver.getNodes(), ' Time:', solver.getTime())
