from typing import List


def bit_map_to_adjacency_list(bitmaps: List[int]) -> List[List[int]]:
  return [
    [i for i in range(len(bitmaps)) if bool((2 ** i) & bitmap)]
    for bitmap in bitmaps
  ]
