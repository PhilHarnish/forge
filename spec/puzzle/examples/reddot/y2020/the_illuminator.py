import random
import time

from spec.puzzle.examples.reddot.y2020 import the_illuminator_data

bit_map = the_illuminator_data.ADJACENCY_BIT_MAP
adjacency_list = the_illuminator_data.ADJACENCY_LIST
target_value = the_illuminator_data.TARGET_VALUE
total = len(bit_map)

def run() -> None:
  reported_progress = 0
  reported_start = time.time()

  def process(
      state: int, visited: int, flipped: int, i: int, allow_off: bool,
      depth: int, acc: float,
  ) -> int:
    nonlocal reported_progress
    increment_total = 1 / (1 << depth)
    increment_i = 0
    increment_sliced = increment_total / ((1 + allow_off) * total)

    # Flip i...
    power = 1 << i
    flipped ^= power
    state ^= bit_map[i]
    # ...see if that worked...
    if state == target_value:
      # Finished.
      return flipped
    # TODO: Peek to see if a future move would erase our local network.
    #    (because if it does then nothing can save us?)
    # ...then, finally, try every neighbor while this bit is on.
    visited_while_on = visited
    for neighbor in adjacency_list[i]:
      maybe_visit = 1 << neighbor
      # Don't repeat work.
      if visited & maybe_visit:
        continue
      visited_while_on |= maybe_visit

      # TODO: hard-coding "True" is not good: everything depends on current
      #   bit state.
      result = process(
          state, visited_while_on, flipped, neighbor, True, depth + 1,
          acc + increment_sliced * increment_i)
      increment_i += 1
      if result:
        return result

    # Did not work, reset state back to off and try 1+ neighbor active.
    state ^= bit_map[i]
    flipped ^= 2 ** i
    # If we're allowed to be off, move to neighbors...
    if allow_off:
      visited_while_off = visited
      for neighbor in adjacency_list[i]:
        maybe_visit = 1 << neighbor
        # Don't repeat work.
        if visited & maybe_visit:
          continue
        visited_while_off |= maybe_visit
        result = process(
            state, visited_while_off, flipped, neighbor, False, depth + 1,
            acc + increment_sliced * increment_i)
        increment_i += 1
        if result:
          return result
    # If after trying each neighbor, neither us or any neighbor was clicked then
    # there will never be a valid solution. Give up.
    acc += increment_total
    if (acc - reported_progress) > .00001:
      reported_progress = acc
      time_elapsed = time.time() - reported_start
      print('%s%% @ %d s elapsed' % (reported_progress * 100, time_elapsed))
    return 0

  i_start = random.randint(0, total - 1)
  visited_start = 1 << i_start
  print('Starting @ %d' % i_start)
  print(process(0, visited_start, 0, i_start, True, 0, 0.0))

if __name__ == '__main__':
  run()
