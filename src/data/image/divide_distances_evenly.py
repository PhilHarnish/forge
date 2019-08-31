import math
from typing import Dict, Iterable, List, Tuple

DEBUG = False


def divide_distances_evenly(
    distances: List[float],
    required_divisions_ratio: float = 1.0,
    max_consecutive_missing: int = 1,
    anchor_resolution_px: float = 1.0,
    division_distance_resolution_px: float = 1,
) -> Tuple[int, int, int, float]:
  n_distances = len(distances)
  assert n_distances >= 2
  assert distances[0] == 0
  assert max_consecutive_missing >= 0

  max_distance = distances[-1]
  # How wide is the largest possible gap given max_consecutive_missing?
  largest_gap_distance = max(b - a for a, b in zip(distances, distances[1:]))
  min_division_distance = largest_gap_distance / (max_consecutive_missing + 1)
  division_distance_resolution = division_distance_resolution_px / max_distance
  required_n_distances_ratio = n_distances / required_divisions_ratio

  best_solution = (0, n_distances - 1, 1, 0.0)
  best_score = float('inf')  # Low is good.

  wasted_distance = {}
  farthest_distance = {}
  scanned_ids = set()

  start_distance = -1
  end_distance = -1
  for start_pos in range(n_distances):
    if start_distance == distances[start_pos]:
      continue  # Duplicate distance.
    start_distance = distances[start_pos]

    for end_pos in range(n_distances - 1, start_pos, -1):
      if end_distance == distances[end_pos]:
        continue  # Duplicate distance.
      end_distance = distances[end_pos]

      utilized_distances = end_pos - start_pos + 1
      wasted_distances = n_distances - utilized_distances
      if wasted_distances > best_score:
        # `wasted_distances` alone would prevent a new best_score.
        # NB: Dynamic `break` is required because best_score improves below.
        break

      mid_distance = end_distance - start_distance
      maximum_legal_divisions = round(min(
          # Satisfying max_consecutive_missing is impossible for large n.
          mid_distance / min_division_distance,
          # Satisfying required_n_distances_ratio is impossible for large n.
          # See _N_DIVISIONS_LEMMA below.
          required_n_distances_ratio * (mid_distance / max_distance),
      ))
      for n_divisions in range(1, maximum_legal_divisions):
        division_distance = mid_distance / n_divisions
        # Calculate the first point which is a multiple of division_distance
        # away from start_pos.
        anchor_distance = start_pos % division_distance
        scan_id = (
          _precision(anchor_distance, anchor_resolution_px),
          _precision(division_distance, division_distance_resolution)
        )
        if scan_id in scanned_ids:
          continue
        scanned_ids.add(scan_id)
        wasted_distance.clear()
        farthest_distance.clear()
        max_divisions = round(max_distance / division_distance)
        last_division = max_divisions
        for scan_pos in range(n_distances):
          scan_distance = distances[scan_pos]
          incremental_distance = scan_distance - start_distance
          division = round(incremental_distance / division_distance)
          if division - last_division > max_consecutive_missing:
            break  # Already missed too many divisions. (Large gap.)
          last_division = division
          # If 100% of the remaining_divisions match will we reach
          # required_divisions_ratio?
          remaining_divisions = max_divisions - division
          remaining_distances = end_pos - scan_pos
          maximum_opportunity = min(remaining_divisions, remaining_distances)
          division_matches = len(wasted_distance)
          projected_divisions_ratio = (
              maximum_opportunity + division_matches) / max_divisions
          if projected_divisions_ratio < required_divisions_ratio:
            break  # Nope. Give up. (Typically near end of list anyways.)
          drift = incremental_distance - division * division_distance
          if division not in wasted_distance:
            wasted_distance[division] = drift
            farthest_distance[division] = drift
          else:
            wasted_distance[division] += drift
            if abs(drift) > abs(farthest_distance[division]):
              farthest_distance[division] = drift
        else:  # No `break` in scan.
          present_divisions = len(wasted_distance)
          divisions_present_ratio = present_divisions / max_divisions
          if divisions_present_ratio < required_divisions_ratio:
            continue
          division_center = (division_distance / 2)
          # Calculate the average direction waste is.
          waste_shift_distances = [
              drift for drift in wasted_distance.values()
                if abs(drift) <= division_center]
          if waste_shift_distances:
            # Move in the direction of the waste ("/2" to center result).
            waste_shift_distance = (sum(
                waste_shift_distances) / len(waste_shift_distances)) / 2
          else:
            waste_shift_distance = 0
          required_divisions = math.ceil(
              (max_divisions+1) * required_divisions_ratio)
          total_waste = sum(
              abs(drift - waste_shift_distance) for drift in _best(
                  wasted_distance, required_divisions))
          total_away = sum(
              abs(drift - waste_shift_distance) for drift in _best(
                  farthest_distance, required_divisions))
          score = wasted_distances + total_waste + total_away
          if score >= best_score:
            continue
          best_score = score
          # Return offset in units the caller can interpret.
          offset = waste_shift_distance / mid_distance
          best_solution = (start_pos, end_pos, n_divisions, offset)
          if DEBUG:
            missed_divisions = max_divisions - present_divisions + 1
            print('wasted_distance', _pretty(wasted_distance))
            print('farthest_distance', _pretty(farthest_distance))
            print(
                '@ %0.2f+%0.2f, with steps of %0.2f: %d divisions,'
                ' %d matches, (%d missing) %d waste,'
                ' (%.02f/div); %s -> %s (of %s) with %s unused\n'
                ' score: %.02f + %s + %.02f = %.02f' % (
                  start_distance, (waste_shift_distance / 2),
                  division_distance, n_divisions,
                  present_divisions, missed_divisions,
                  total_waste, total_waste / n_divisions,
                  start_pos, end_pos, n_distances, wasted_distances,
                  # Score:
                  total_waste, wasted_distances, total_away,
                  score,
                ))
  return best_solution


def _best(src: Dict[int, float], max_len: int) -> Iterable[float]:
  values = sorted(src.values())
  return values[:max_len]


def _pretty(c: dict) -> str:
  return ', '.join('%s: %d' % i for i in sorted(c.items()))


def _precision(i: float, resolution: float) -> int:
  return round(i / resolution)


_N_DIVISIONS_LEMMA = """
If we assume all intermediate points are evenly spaced how many
divisions could they possibly cover?
E.g.: 0 [1] 2 3 4 [5] 6
mid_distance / n_divisions = division_distance
max_distance / division_distance = max_divisions
n_distances / max_divisions >= required_div_ratio
3 / (5 / (7 / 11))
n_distances / (max_distance / (mid_distance / n_divisions)) >= required_div_ratio
n_distances / ((n_divisions * max_distance) / mid_distance)) >= required_div_ratio
(n_distances * mid_distance) / (n_divisions * max_distance) >= required_div_ratio
(n_distances * mid_distance) / required_div_ratio >= n_divisions * max_distance
(n_distances * mid_distance) / (required_div_ratio * max_distance) >= n_divisions
(n_distances / required_div_ratio) * (mid_distance / max_distance) >= n_divisions
"""
