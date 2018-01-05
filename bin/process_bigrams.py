# Intended to be used with count_2w.txt which has the following format:
# A B\tFREQENCY
# Sometimes "A" is "<S>" for start and "</S>" for end.
# Output is similar with all output lower-cased (including "<S>" and "</S>").
import collections

from src.data import data

all_results = collections.defaultdict(int)

for line in data.open_project_path('data/count_2w.txt', errors='ignore'):
  a, b, count = line.split()
  key = ('%s %s' % (a, b)).lower()
  all_results[key] += int(count)

for item in sorted(all_results.items(), key=lambda x: x[1], reverse=True):
  print('%s\t%s' % item)
