import collections
import itertools

from data.convert import deep
from data.seek_sets import base_seek_set

# Wordsearch rules.
SEARCH = object()
# Compas (NSEW) directions.
COMPASS = object()
# Right & down directions.
READING = object()
# Column-by-column: return results from one column of grid at a time.
COLUMN = object()
# Row-by-row: return results from one row of grid at a time.
ROW = object()
# Knights tour: return characters using knight L shape moves.
KNIGHT = object()
# Snake: allow arbitrary turns.
SNAKE = object()


class GridSeekSet(base_seek_set.BaseSeekSet):
  def __init__(
      self, grid, mode=SEARCH, start_row=None, start_column=None, goal_row=None,
      goal_column=None):
    """Produce letters from a grid.

    :param grid: Input 2D array of characters.
    :param mode: Method for searching grid. Default to "SEARCH" which has
        usual word search behavior.
    :param start_row: Starting position for search. Undefined is anywhere.
    :param start_column: Starting position for search. Undefined is anywhere.
    :param goal_row: Starting position for end. Undefined is anywhere.
    :param goal_column: Starting position for end. Undefined is anywhere.
    """
    super(GridSeekSet, self).__init__(set())
    self._grid = deep.lower(grid)
    self._index = self._index_grid(grid)
    self._mode = mode
    self._start_row = start_row
    self._start_column = start_column
    self._goal_row = goal_row
    self._goal_column = goal_column

  def __len__(self):
    return len(self._grid) * len(self._grid[0])

  def _index_grid(self, grid):
    result = collections.defaultdict(list)
    for r, row in enumerate(grid):
      for c, col in enumerate(row):
        if isinstance(col, set):
          for i in col:
            result[i].append((r, c))
        else:
          result[col[0]].append((r, c))
    return result

  def seek(self, seek):
    results, starts = self._starts(seek)
    if results:
      return results
    # Find `start` in self._index to begin search.
    for row, col in starts:
      self._seek(seek, results, [(row, col)])
    return results

  def _seek(self, seek, results, path):
    row, col = path[-1]
    cursor = self._grid[row][col]
    offset = _offset(cursor, seek)
    if offset < 0:
      return
    seek = seek[offset:]
    if not seek and offset < len(cursor):
      # `seek` matched `cursor` but some of `cursor` remains.
      if isinstance(cursor, set):
        results.update(cursor)
      else:
        results.add(cursor[offset])
      return
    for row_next, col_next in self._directions(path):
      if not self._valid(row, col, row_next, col_next):
        continue
      path.append((row_next, col_next))
      self._seek(seek, results, path)
      path.pop()

  def _starts(self, seek):
    results = set()
    if seek:
      return results, self._index[seek[0]]
    if self._start_row is not None and self._start_column is not None:
      return results, [(self._start_row, self._start_column)]
    if self._mode in (COMPASS, KNIGHT, SEARCH, SNAKE, READING):
      results.update(self._index.keys())
      return results, []
    elif self._mode == COLUMN:
      for row in self._grid:
        results.add(row[0][0])  # First letter of first row entry.
      return results, []
    elif self._mode == ROW:
      for c in self._grid[0]:
        results.add(c[0])  # First letter of first row entry.
      return results, []
    return results, []

  def _directions(self, path):
    y, x = path[-1]  # x, y = row, col.
    if self._mode in (SEARCH, SNAKE):
      if len(path) == 1 or self._mode == SNAKE:
        # Any direction from start is valid.
        for dx, dy in itertools.product([-1, 0, 1], [-1, 0, 1]):
          yield y + dy, x + dx
        return
      # Continue in direction already headed.
      y_previous, x_previous = path[-2]
      yield y + (y - y_previous), x + (x - x_previous)
    elif self._mode == COMPASS:
      # North, south, east and west are valid.
      for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
        yield y + dy, x + dx
    elif self._mode == READING:
      if len(path) == 1:
        # Right and down are valid.
        for dx, dy in [(0, 1), (1, 0)]:
          yield y + dy, x + dx
        return
      # Continue in direction already headed.
      y_previous, x_previous = path[-2]
      yield y + (y - y_previous), x + (x - x_previous)
    elif self._mode == COLUMN:
      for new_y in range(len(self._grid)):
        yield new_y, x + 1
    elif self._mode == ROW:
      for new_x in range(len(self._grid[y])):
        yield y + 1, new_x
    elif self._mode == KNIGHT:
      for dx, dy in itertools.product([-1, -2, 1, 2], [-1, -2, 1, 2]):
        if abs(dx) == abs(dy):
          continue
        yield y + dy, x + dx
    else:
      raise NotImplementedError(self._mode)

  def _valid(self, row, col, row_next, col_next):
    if (row, col) == (row_next, col_next):
      return False
    if row_next < 0 or col_next < 0:
      return False
    if row_next >= len(self._grid) or col_next >= len(self._grid[row_next]):
      return False
    return True

  def _slice(self, start, stop, step):
    if not isinstance(start, str):
      return super(GridSeekSet, self)._slice(start, stop, step)
    raise NotImplementedError()


def _offset(source, sink):
  """Finds common prefix, if any, and returns offset after alignment."""
  if not sink:
    return 0
  if isinstance(sink, list):
    sink = ''.join(sink)
  if isinstance(source, set):
    if sink[0] in source:
      return 1
    return -1
  source_length = len(source)
  sink_length = len(sink)
  if source_length > sink_length:
    if not source.startswith(sink):
      # Dead end: sink was not found in source.
      return -1
    return sink_length  # sink[sink_length:] == ''.
  elif not sink.startswith(source):
    # Dead end: sink was not found in source.
    return -1
  return source_length
