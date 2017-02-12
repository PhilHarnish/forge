import os

from src.origen import seven_segment

_alphabet = None
_this_path = os.path.dirname(os.path.realpath(__file__))
_base_path = os.path.join(_this_path.split('/forge/')[0], 'forge')

def _read(project_path):
  abs_path = os.path.join(_base_path, project_path)
  return open(abs_path).read()

def alphabet():
  global _alphabet
  if not _alphabet:
    _alphabet = seven_segment.load(_read('data/seven_segment_alphabet.txt'))
  return _alphabet
