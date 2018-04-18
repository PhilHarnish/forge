import collections
import contextlib
import heapq
import subprocess
from typing import Dict, Iterable, TextIO, Tuple

from data import data, process_common

SRCS_PATTERN = 'data/corpus/g1m_ngram/googlebooks-eng-1M-1gram-20090715-%s.csv'
AGGREGATED_PATTERN = 'data/corpus/g1m_ngram/aggregated-1gram-20090715-%s.csv'
SORTED_PATTERN = 'data/corpus/g1m_ngram/sorted-1gram-20090715-%s.csv'
MERGED_OUT_PATTERN = 'data/g1m_1gram.txt'
MERGED_OUT_SORTED_PATTERN = 'data/g1m_sorted_1gram.txt'
PROPER_NOUN_OUT_PATTERN = 'data/g1m_proper_1gram.txt'
PROPER_NOUN_OUT_SORTED_PATTERN = 'data/g1m_proper_sorted_1gram.txt'

SCREEN_FILE = 'data/clues_processed.txt'
SCREEN_THRESHOLD = 400


def get_screen() -> Dict[str, float]:
  results = {}
  with data.open_project_path(SCREEN_FILE, mode='r') as screen:
    lines = [line for line in screen]
    count = len(lines)
    for i, line in enumerate(lines):
      word, score = line.split()
      if int(score) <= SCREEN_THRESHOLD:
        break
      results[word] = .1 + (1 - (i / count)) * .9
  return results


@contextlib.contextmanager
def open_shards(pattern: str, mode: str) -> Dict[str, TextIO]:
  results = {}
  for c in 'abcdefghijklmnopqrstuvwxyz':
    results[c] = data.open_project_path(pattern % c, mode=mode)
  yield results
  for fp in results.values():
    fp.close()


def aggregate() -> None:
  screen = get_screen()
  with open_shards(pattern=AGGREGATED_PATTERN, mode='w') as outs:
    for i in range(9+1):
      results = collections.defaultdict(int)
      print('reading', SRCS_PATTERN % i)
      for line in data.open_project_path(SRCS_PATTERN % i, errors='ignore'):
        if not line[0].isalpha():
          continue
        word, year, count, _, _ = line.split('\t')
        canonicalized = word.lower()
        year = int(year)
        count = int(count)
        word_score = process_common.score(word, count, year)
        if not word_score:
          continue
        if canonicalized in screen:
          word_score = int(screen[canonicalized] * word_score)
        else:
          word_score //= 100
        if not word_score:
          continue
        results[canonicalized] += word_score
        if canonicalized.endswith("'s"):
          results[canonicalized[:-2] + 's'] += word_score
      print('aggregating', SRCS_PATTERN % i)
      for key, value in results.items():
        outs[key[0]].write('%s\t%s\n' % (key, value))


def sort_and_sum() -> None:
  with open_shards(pattern=SORTED_PATTERN, mode='w') as outs:
    with open_shards(pattern=AGGREGATED_PATTERN, mode='r') as srcs:
      for c, src in srcs.items():
        results = collections.defaultdict(int)
        print('sorting', c)
        for line in src:
          word, count = line.rstrip('\n').split('\t')
          count = int(count)
          results[word] += count
        print('writing', c)
        for key, value in sorted(
            results.items(), key=lambda x: x[1], reverse=True):
          outs[c].write('%s\t%s\n' % (key, value))


def _merge_srcs_iter() -> Iterable[Tuple[str, int]]:
  def word_stream(stream: TextIO) -> Iterable[Tuple[str, int]]:
    for line in stream:
      word, count = line.split()
      count = int(count)
      yield word, count
  with open_shards(pattern=SORTED_PATTERN, mode='r') as srcs:
    streams = [word_stream(fp) for fp in srcs.values()]
    yield from heapq.merge(*streams, key=lambda x: x[1], reverse=True)


def merge() -> None:
  merged_lines = _merge_srcs_iter()
  print('writing merged')
  with data.open_project_path(MERGED_OUT_PATTERN, mode='w') as out:
    for result in merged_lines:
      word, weight = result
      if weight <= 75:  # Chosen arbitrarily below "gherkin".
        break
      out.write('%s\t%s\n' % (word, weight))
  print('writing merged, proper nouns')
  with data.open_project_path(
      PROPER_NOUN_OUT_PATTERN, mode='w') as proper_nouns:
    for word, weight in reversed([
        (word, weight) for word, weight in merged_lines if weight < -75]):
      proper_nouns.write('%s\t%s\n' % (word, -weight))


def alphasort() -> None:
  print('sorting unigrams')
  with data.open_project_path(MERGED_OUT_SORTED_PATTERN, mode='w') as out:
    subprocess.call(['sort', data.project_path(MERGED_OUT_PATTERN)], stdout=out)
  print('sorting proper unigrams')
  with data.open_project_path(PROPER_NOUN_OUT_SORTED_PATTERN, mode='w') as out:
    subprocess.call(
        ['sort', data.project_path(PROPER_NOUN_OUT_PATTERN)], stdout=out)


def main() -> None:
  aggregate()
  sort_and_sum()
  merge()
  alphasort()


main()
