import math
from typing import List, Tuple


def cluster_distances_evenly(
    distances: List[float], required_divisions_ratio: float
) -> Tuple[int, int, int]:
  print(distances)
  full_distance = distances[-1]
  n_distances = len(distances)
  scan_matches = {}
  farthest_matches = {}
  wasted_distance = {}
  acc_wasted_distance = 0
  best_delta = float('inf')
  best_result = (-1, -1, -1)
  end_pos = int(n_distances * required_divisions_ratio)
  for initial_pos, initial_distance in enumerate(distances):
    if initial_pos >= end_pos:
      break
    initial_wasted_distance = acc_wasted_distance - (
        initial_pos * initial_distance)
    acc_wasted_distance += initial_distance
    remaining_distances = n_distances - initial_pos
    remaining_distance = full_distance - initial_distance
    maximum_remaining_divisions = remaining_distances // required_divisions_ratio
    # Assuming pt was the start of a pattern...
    # Consider each further point as a continuation for that pattern.
    next_pos = initial_pos + 1
    while next_pos < n_distances:
      next_distance = distances[next_pos]
      next_pos += 1
      division_distance = next_distance - initial_distance
      if not division_distance:
        continue
      n_divisions = math.ceil(remaining_distance / division_distance)
      if n_divisions > maximum_remaining_divisions:
        # This point is so close it would require too many missing lines.
        continue
      scan_pos = next_pos
      scan_matches.clear()
      scan_matches[0] = 0
      scan_matches[1] = 0
      farthest_matches.clear()
      farthest_matches[0] = initial_distance  # Penalize starting deep in list.
      wasted_distance.clear()
      wasted_distance[0] = initial_wasted_distance
      last_matching_pos = None
      while scan_pos < n_distances:
        scan_distance = distances[scan_pos]
        incremental_scan_distance = scan_distance - initial_distance
        scan_pos += 1
        # Determine which division this point would be closest to.
        scan_division = int(round(incremental_scan_distance / division_distance))
        if scan_division < 0:
          print('wtf', scan_distance, initial_distance, incremental_scan_distance, division_distance)
        # Store this point's accuracy as the scan_division'th division.
        scan_drift = scan_division * division_distance - scan_distance
        scan_delta = abs(scan_drift)
        if scan_division not in wasted_distance:
          wasted_distance[scan_division] = scan_drift
        else:
          wasted_distance[scan_division] += scan_drift
        if (scan_division not in farthest_matches or
            scan_delta > farthest_matches[scan_division]):
          farthest_matches[scan_division] = scan_delta
        if (scan_division not in scan_matches or
            scan_delta < scan_matches[scan_division]):
          scan_matches[scan_division] = scan_delta
          last_matching_pos = scan_pos - 1  # Undo increment.
        # Not safe: multiple points may "slop".
        #if (scan_division + 1) * division_distance > full_distance:
        #  break  # Impossible to discover any more relevant points.
      if not last_matching_pos:
        continue
      matched_divisions = len(scan_matches)
      required_divisions = n_divisions * required_divisions_ratio
      if matched_divisions < required_divisions:
        # division_distance has too few matches when starting at initial_pos.
        continue
      assert last_matching_pos, '1+ matches are required'
      missing_divisions = n_divisions - (matched_divisions - 1)  # HACK: Do not count endpoint 2x.
      division_total_delta = sum(delta for delta in scan_matches.values()) + (
          missing_divisions * division_distance)
      #total_slop = sum(
      #    delta for i, delta in farthest_matches.items() if delta > scan_matches[i])
      total_slop = sum(abs(delta) for delta in wasted_distance.values())
      delta_per_division = (total_slop + division_total_delta) / n_divisions
      if delta_per_division < best_delta:
        print(repr(scan_matches))
        print(repr(farthest_matches))
        print(repr(wasted_distance))
        print(
            '@ %0.2f, with steps of %0.2f: %d divisions, %d matches,'
            ' (%d missing) %s delta (%0.2f/div), %s slop (%.02f/div)\n'
            ' score = %.02f' % (
              initial_distance, division_distance, n_divisions,
              matched_divisions, missing_divisions,
              division_total_delta, division_total_delta / n_divisions,
              total_slop, total_slop / n_divisions,
              delta_per_division
            ))
        best_delta = delta_per_division
        best_result = (initial_pos, last_matching_pos, n_divisions)
  return best_result
