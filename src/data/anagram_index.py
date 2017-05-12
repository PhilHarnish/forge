import collections
import functools
import re


class AnagramIndex(dict):
  def __init__(self, data):
    indexed = collections.defaultdict(set)
    for key in data:
      indexed[''.join(sorted(key))].add(key)
    super(AnagramIndex, self).__init__(indexed)

  def __setitem__(self, key, value):
    raise NotImplementedError()

  def __getitem__(self, item):
    return super(AnagramIndex, self).__getitem__(''.join(sorted(item)))

  def __contains__(self, item):
    return super(AnagramIndex, self).__contains__(''.join(sorted(item)))
