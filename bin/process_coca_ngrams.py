import gzip
import shutil
from typing import Dict, Iterable, List, TextIO

from data import data, process_common

UNIGRAM_REFERENCE = 'data/g1m_1gram.txt'
SRCS_PATTERN = 'data/corpus/coca/w%s_.txt'
OUTS_PATTERN = 'data/coca_%sgram.txt'
GZIP_PATTERN = 'data/coca_%sgram.gz'
REFERENCE = {}
WEIGHTS = {}


def load_reference() -> None:
  with data.open_project_path(UNIGRAM_REFERENCE, mode='r') as src:
    for line in src:
      word, score = line.split()
      score = int(score)
      REFERENCE[word] = score


def aggregate() -> None:
  print('reading & aggregating')
  iterables = [screen([])] + [
    screen(data.open_project_path(SRCS_PATTERN % i, mode='r', errors='ignore'))
    for i in range(2, 5+1)
  ]
  outputs = [
    data.open_project_path(OUTS_PATTERN % i, mode='w')
    for i in range(2, 5 + 1)
  ]
  position = ''
  for prefix, suffix in process_common.aggregate_prefixes(iterables):
    if prefix[0] != position:
      print(prefix[0], end=', ')
      position = prefix[0]
    share(WEIGHTS[prefix], REFERENCE[prefix], suffix, outputs, 0)
    del WEIGHTS[prefix]  # Done with this entry.
  print()

def screen(iterable: Iterable[str]) -> Iterable[str]:
  for line in iterable:
    count, *words = line.split()
    if not all(word in REFERENCE for word in words):
      continue
    if any(process_common.score(word, 100, 0) < 100 for word in words):
      continue
    first = words[0]
    key = ' '.join(words)
    if first not in WEIGHTS:
      WEIGHTS[first] = {}
    WEIGHTS[first][key] = int(count)
    yield key


def share(
    weights: Dict[str, int], total: int, results: list, outputs: List[TextIO],
    pos: int) -> None:
  output = outputs[pos]
  min_weight = min(weights.get(ngram, total) for ngram, _ in results)
  denominator = sum(weights.get(ngram, min_weight) for ngram, _ in results)
  if denominator:
    layer_scale = total / denominator
  else:
    layer_scale = 1
  for ngram, children in results:
    weight = int(layer_scale * weights.get(ngram, min_weight))
    if children:
      share(weights, weight, children, outputs, pos + 1)
    output.write('%s\t%d\n' % (ngram, weight))


def compress() -> None:
  print('compressing')
  files = [
    (
      GZIP_PATTERN % i,
      data.open_project_path(OUTS_PATTERN % i, mode='rb'),
      gzip.open(data.project_path(GZIP_PATTERN % i), mode='wb'),
    ) for i in range(2, 5 + 1)
  ]
  for name, f_in, f_out in files:
    print(name)
    shutil.copyfileobj(f_in, f_out)


def main() -> None:
  load_reference()
  aggregate()
  compress()
  print('complete')

main()
