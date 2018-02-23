import itertools
from typing import Iterable

BASE_ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
WORD_SEPARATOR = ' '
EXTRA = "'"
SEPARATOR = WORD_SEPARATOR


# Should letter frequency ('etaoinshrdlcumwfgypbvkjxqz') be used instead?
_ALPHA_CHARACTERS = BASE_ALPHABET + WORD_SEPARATOR + EXTRA
SIZE = len(_ALPHA_CHARACTERS)
_ALPHA_MAP = {
  c: 2**i for i, c in enumerate(_ALPHA_CHARACTERS)
}
_ALPHA_ARRAY = [_ALPHA_MAP.get(chr(c), 0) for c in range(128)]



def bits(mask: int) -> Iterable[int]:
  while mask:
    next_available = mask & (mask - 1)
    yield mask - next_available
    mask = next_available


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
