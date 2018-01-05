import collections

from data import data, process_common

SRC = 'data/clues.txt'
OUT = 'data/clues_processed.txt'


def process() -> None:
  results = collections.defaultdict(int)
  with data.open_project_path(SRC, mode='r', errors='ignore') as src:
    for line in src:
      word, _, year, *remainder = line.split()
      word = word.lower()
      try:
        year = int(year)
      except:
        continue
      score = process_common.score(word, 100, year)
      if score:
        results[word] += score
  with data.open_project_path(OUT, mode='w') as out:
    for word, score in sorted(
        results.items(), key=lambda x: x[1], reverse=True):
      out.write('%s\t%s\n' % (word, score))


def main() -> None:
  process()


main()
