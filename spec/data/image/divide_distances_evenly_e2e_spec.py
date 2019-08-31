import itertools

from data.image import divide_distances_evenly
from spec.mamba import *


def division_distance(
    distances: List[float], start: int, end: int, n_divisions: int,
    offset: float) -> float:
  del offset
  return (distances[end] - distances[start]) / n_divisions


def expect_distances_similar(distances: List[List[float]]) -> None:
  division_distances = [
    division_distance(
        d, *divide_distances_evenly.divide_distances_evenly(d, 0.75)
    ) for d in distances
  ]
  for a, b in itertools.combinations(division_distances, 2):
    expect(a).to(be_close_to(b, relative_tolerance=0.04))


with description('divide_distances_evenly', 'end2end'):
  with it('askew.png'):
    distance_dimensions = [
      [  # 0 degrees.
        0, 2.19, 2.84, 5, 24.43, 26, 27.84, 28.2, 29, 52, 53.85, 54.2, 55, 78,
        79.85, 80.2, 81, 104, 107.21, 109, 132, 132.86, 133.21, 135, 157,
        158.22, 158.86, 161, 178.91, 180.52, 183, 184.87, 185.22, 187, 203.9,
        205.54, 205.84, 207.22, 208, 210.22, 213,
      ],
      [  # 60 degrees.
        0, 4, 26, 30, 52, 56, 78, 81, 103, 108, 130,
        132.63, 134, 156, 160, 182, 184, 186, 208, 212,
      ],
      [  # 120 degrees.
        0, 2.23, 2.75, 5, 26, 28.23, 28.76, 30, 52, 53.76, 54.24, 55, 78, 80.77,
        81.24, 104, 105.25, 105.77, 109, 130, 132, 132.25, 132.77, 134, 158,
        158.25, 158.78, 160, 182, 184.26, 184.78, 186, 208, 210.26, 210.79, 213,
      ],
    ]
    expect_distances_similar(distance_dimensions)

  with it('kakuro.png'):
    distance_dimensions = [
      [  # 0 degrees.
        0, 32, 32.7, 34, 105.71, 106.2, 107, 141.71, 142, 142.21, 212.72, 214,
        215.22, 250, 250.23, 321, 321.74, 322.24, 323, 357,
      ],
      [  # 90 degrees.
        0, 32, 34, 34.48, 106, 106.5, 140, 141.41, 142, 142.5, 213.51, 214,
        214.42, 215.51, 249.43, 250, 250.52, 321, 321.44, 322.53, 357, 395,
      ],
    ]
    expect_distances_similar(distance_dimensions)

  with it('multi.png'):
    distance_dimensions = [
      [  # 0 degrees.
        0, 2, 31, 64, 96, 99, 128, 160, 191, 224, 256, 288,
      ],
      [  # 90 degrees.
        0, 3, 32, 64, 97, 97.27, 99, 128, 160, 192, 193.8, 195, 224, 256, 288,
      ],
    ]
    expect_distances_similar(distance_dimensions)

  with it('pathfinder.png'):
    distance_dimensions = [
      [  # 0 degrees.
        0, 104, 148, 197, 202, 253, 295, 399, 443, 492, 497, 548, 590, 694, 738,
        786, 790, 841, 885,
      ],
      [  # 60 degrees.
        0, 44, 93, 98, 148, 191, 295, 339, 388, 393, 443, 486, 590, 634, 683,
        688, 738, 781,
      ],
      [  # 120 degrees.
        0, 42, 94, 99, 148, 192, 295, 337, 389, 394, 443, 487, 590, 632, 684,
        689, 738, 782,
      ],
    ]
    expect_distances_similar(distance_dimensions)

  with it('rowsgarden.png'):
    distance_dimensions = [
      [0, 69, 139, 207, 278, 347, 416, 485],  # 30 degrees.
      [
        0, 40, 45, 110, 115, 181, 186, 251, 256, 322, 326, 392, 397, 462, 467,
        533, 538, 603, 608, 675, 678, 744, 749, 789,  # 90 degrees.
      ],
      [0, 69, 139, 208, 277, 347, 416, 486],  # 150 degrees.
    ]
    expect_distances_similar(distance_dimensions)
