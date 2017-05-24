# coding: utf-8

import os

_this_path = os.path.dirname(os.path.realpath(__file__))
_base_path = os.path.join(_this_path.split('/forge/')[0], 'forge')


def _read_lines(project_path):
  abs_path = os.path.join(_base_path, project_path)
  return open(abs_path).read().split('\n')


words = frozenset([
  word for word in _read_lines('data/words.txt')
])

u"""
ɪ = ih (sit)
ɛ = eh (bed)
l ?
v ?
z
ɪ = ih (sit, wind)
k
t
"""
ALL = set('bdglmnprstw')
HAS = set('tv')
BAD = (ALL - HAS)  # | {'f', 'ph'}
HAS_ENDING = ''  # 'y'
BAD_ENDINGS = [
  'tion',
]

for word in sorted(words):
  if (all([word.count(c) == 1 for c in HAS]) and
    all([word.count(c) == 0 for c in BAD]) and
    (not HAS_ENDING or word.endswith(HAS_ENDING)) and
    not any([word.endswith(ending) for ending in BAD_ENDINGS])):
    print(word)
