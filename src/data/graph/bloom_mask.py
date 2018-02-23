import itertools
from typing import Iterable, List

from util import perf

BASE_ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
UNIT_SEPARATOR = chr(31)
WORD_SEPARATOR = ' '
EXTRA = "'"
SEPARATOR = {UNIT_SEPARATOR, WORD_SEPARATOR}
ALPHA_CHARACTERS = BASE_ALPHABET + WORD_SEPARATOR + EXTRA
SIZE = len(ALPHA_CHARACTERS)

# Should letter frequency ('etaoinshrdlcumwfgypbvkjxqz') be used instead?
_ALPHA_MAP = {
  c: 1 << i for i, c in enumerate(ALPHA_CHARACTERS)
}
_ALPHA_MAP[UNIT_SEPARATOR] = _ALPHA_MAP[' ']
_ALPHA_ARRAY = [_ALPHA_MAP.get(chr(c), 0) for c in range(128)]
_INDEX_MAP = {
  c: i for i, c in enumerate(ALPHA_CHARACTERS)
}
_INDEX_ARRAY = [_INDEX_MAP.get(chr(c), -1) for c in range(128)]
_POW_MAP = {
  1 << i: i for i in range(SIZE)
}


bits = perf.Perf('bits', ['yield', 'list', 'blocks'])
indexes = perf.Perf('indexes', ['map', 'blocks'])
everything = perf.Perf('BloomNode', ['dict', 'list'])


@bits.profile('yield')
def bits(mask: int) -> Iterable[int]:
  while mask:
    next_available = mask & (mask - 1)
    yield mask - next_available
    mask = next_available


@bits.profile('list')
def bits(mask: int) -> Iterable[int]:
  result = []
  while mask:
    next_available = mask & (mask - 1)
    result.append(mask - next_available)
    mask = next_available
  return result


def _get_bit_blocks() -> List[List[int]]:
  blocks = []
  for i in range(_BIT_BLOCK + 1):
    block = []
    blocks.append(block)
    while i:
      next_available = i & (i - 1)
      block.append(i - next_available)
      i = next_available
  return blocks


_BIT_WIDTH = 6
_BIT_BLOCK = (1 << _BIT_WIDTH) - 1
_BIT_BLOCKS = _get_bit_blocks()


@bits.profile('blocks')
def bits(mask: int) -> Iterable[int]:
  offset = 0
  while mask:
    yield from [i << offset for i in _BIT_BLOCKS[mask & _BIT_BLOCK]]
    mask >>= _BIT_WIDTH
    offset += _BIT_WIDTH


def index_of(character: str) -> int:
  if len(character) != 1:
    raise ValueError('Only provide 1 character ("%s" given)' % character)
  o = ord(character)
  if o < 128:
    result = _INDEX_ARRAY[o]
    if result >= 0:
      return result
  raise NotImplementedError('Unable to get index for "%s"' % character)


def _get_index_blocks() -> List[List[int]]:
  blocks = []
  for i in range(_INDEX_BLOCK + 1):
    block = []
    blocks.append(block)
    while i:
      next_available = i & (i - 1)
      block.append(_POW_MAP[i - next_available])
      i = next_available
  return blocks


_INDEX_WIDTH = 8
_INDEX_BLOCK = (1 << _INDEX_WIDTH) - 1
_INDEX_BLOCKS = _get_index_blocks()


@indexes.profile('map')
def indexes(mask: int) -> Iterable[int]:
  while mask:
    next_available = mask & (mask - 1)
    yield _POW_MAP[mask - next_available]
    mask = next_available


@indexes.profile('blocks')
def indexes(mask: int) -> Iterable[int]:
  result = []
  offset = 0
  while mask:
    yield from [i + offset for i in _INDEX_BLOCKS[mask & _INDEX_BLOCK]]
    mask >>= _INDEX_WIDTH
    offset += _INDEX_WIDTH
  return result


def for_alpha(character: str) -> int:
  if len(character) != 1:
    raise ValueError('Only provide 1 character ("%s" given)' % character)
  o = ord(character)
  if o < 128:
    result = _ALPHA_ARRAY[o]
    if result:
      return result
  raise NotImplementedError('Unable to compute mask for "%s"' % character)


def lengths_product(a: int, b: int, duplicates: int = 1) -> int:
  """Combine lengths a and b, with b optionally repeated duplicates times.

  Algorithm is a*(b**duplicates) where summation is replaced with bitwise OR
  and b**duplicates is calculated in log2 time by multiplying results together.
  """
  if not a or not b or not duplicates:
    return 0
  # Accumulate products for a * b * b * b * b ... etc.
  result = a
  # First, b**duplicates:
  pow_low = 1
  acc = b
  for pow_hi in bits(duplicates):  # 1, 2, 4, 8, ... etc.
    while pow_low < pow_hi:
      # Raise acc to pow_hi power.
      pow_low <<= 1
      acc_next = acc
      acc = 0
      for x, y in itertools.product(bits(acc_next), bits(acc_next)):
        acc |= x * y
    # acc ~= b * pow_hi, multiply into result.
    result_next = result
    result = 0
    for x, y in itertools.product(bits(result_next), bits(acc)):
      result |= x * y
  return result


def map_to_str(provide_mask: int, require_mask: int) -> str:
  blocks = []
  for group in (BASE_ALPHABET, WORD_SEPARATOR+EXTRA):
    block = []
    for c in group:
      mask = for_alpha(c)
      if require_mask and require_mask & mask:
        if c == ' ':
          block.append(' !')
        else:
          block.append(c.upper())
      elif provide_mask and provide_mask & mask:
        block.append(c)
    if block:
      blocks.append(''.join(block))
  return ';'.join(blocks)


def normalize(string: str) -> str:
  return string.replace(UNIT_SEPARATOR, ' ')


class BitMatchAnything(int):
  def __and__(self, other: int) -> int:
    return other

  def __rand__(self, other: int) -> int:
    return other

  def __or__(self, other: int) -> int:
    return other

  def __ror__(self, other: int) -> int:
    return other

  def __eq__(self, other: int) -> bool:
    return True


PROVIDE_NOTHING = BitMatchAnything()
REQUIRE_NOTHING = BitMatchAnything()
ANY_LENGTHS = BitMatchAnything()
