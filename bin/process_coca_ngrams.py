from data import data, process_common

UNIGRAM_REFERENCE = 'data/g1m_1gram.txt'
SRCS_PATTERN = 'data/corpus/coca/w%s_.txt'
OUTS_PATTERN = 'data/coca_%sgram.txt'
REFERENCE = {}


def load_reference() -> None:
  with data.open_project_path(UNIGRAM_REFERENCE, mode='r') as src:
    for line in src:
      word, score = line.split()
      score = int(score)
      REFERENCE[word] = score


def sort_key(x) -> tuple:
  count, words = x
  return count, REFERENCE[words[0]]


def aggregate(i: int) -> None:
  results = []
  print('reading', SRCS_PATTERN % i)
  with data.open_project_path(
      SRCS_PATTERN % i, mode='r', errors='ignore') as src:
    for line in src:
      count, *words = line.split()
      count = int(count)
      if not all(word in REFERENCE for word in words):
        continue
      if any(process_common.score(word, 100, 0) < 100 for word in words):
        continue
      results.append((count, words))
  total = len(results)
  print('writing', OUTS_PATTERN % i)
  with data.open_project_path(OUTS_PATTERN % i, mode='w') as out:
    for i, (count, words) in enumerate(
        sorted(results, key=sort_key, reverse=True)):
      pos = total - i
      score = (pos + count) // 2  # Average of position & score.
      out.write('%s\t%s\n' % (' '.join(words), score))


def main() -> None:
  load_reference()
  for i in range(2, 5+1):
    aggregate(i)

main()
