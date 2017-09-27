import collections

from data import trie
from data.seek_sets import base_seek_set


class ChainSeekSet(base_seek_set.BaseSeekSet):
  def __init__(self, sets, length, offset='', prefix=''):
    """Chains `sets` together while seeking.

    :param sets: list of str.
    :param length: target length to emulate.
    :param offset: pre-seek offset.
    :param prefix: required start to seek operations.
    """
    if not isinstance(sets, list):
      raise TypeError('ChainSeekSet `sets` must be list')
    if length < 0:
      raise ValueError('Target length (%s) invalid' % length)
    elif sum(map(len, sets)) < length:
      raise ValueError('Input sets (%s) smaller than target length (%s)' % (
          sets, length))
    super(ChainSeekSet, self).__init__(sets)
    self._start = set(self._sets)
    l = len(self._sets)
    self._id_to_set = dict((l - i, s) for i, s in enumerate(self._sets))
    self._set_to_ids = collections.defaultdict(list)
    trie_input = []
    for i, s in self._id_to_set.items():
      if s not in self._set_to_ids:
        trie_input.append((s, i))
      self._set_to_ids[s].append(i)
    self._trie = trie.Trie(trie_input)
    self._length = length
    self._offset = offset
    self._prefix = prefix

  def __len__(self):
    return self._length

  def set_length(self, length):
    self._length = length

  def seek(self, seek):
    if isinstance(seek, list):
      seek = ''.join(seek)
    seek_length = len(seek)
    prefix_length = len(self._prefix)
    if not prefix_length:
      pass
    elif prefix_length > seek_length:
      if self._prefix.startswith(seek):
        # Return the next character in `self._prefix` as only result.
        return self._prefix[len(seek)]
      return ''
    elif seek.startswith(self._prefix):
      #seek = seek[prefix_length:]
      pass
    else:
      return ''  # Seek does not match prefix.
    return self._seek(self._offset + seek, set(), set())

  def _seek(self, seek, used, result):
    seek_length = len(seek)
    # First, add partial matches.
    for i, s in self._id_to_set.items():
      if i in used:
        continue
      if len(s) > seek_length and s.startswith(seek):
        result.add(s[seek_length])
    # For any complete match, recurse.
    for match, _ in self._trie.walk(seek):  # exact_match=True?
      remaining = seek[len(match):]
      for i in self._set_to_ids[match]:
        if i in used:
          continue
        used.add(i)
        self._seek(remaining, used, result)
        used.remove(i)
    return result

  def _slice(self, start, stop, step):
    if not isinstance(start, str):
      return super(ChainSeekSet, self)._slice(start, stop, step)
    start_length = len(start)
    prefix_length = len(self._prefix)
    if not prefix_length:
      prefix = ''  # No prefix.
    elif prefix_length > start_length:
      if self._prefix.startswith(start):
        # The new prefix begins where start leaves off.
        prefix = self._prefix[len(start):]
      else:
        raise ValueError('Start ("%s") does not match prefix ("%s")' % (
          start, self._prefix))
    elif start.startswith(self._prefix):
      prefix = ''  # Prefix consumed.
    else:
      raise ValueError('Start ("%s") does not match prefix ("%s")' % (
        start, self._prefix))
    return ChainSeekSet(
        self._sets, self._length - len(start),
        offset=self._offset + start,
        prefix=prefix)
