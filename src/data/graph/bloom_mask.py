BASE_ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
UNIT_SEPARATOR = chr(31)
WORD_SEPARATOR = ' '
UPPER_ALPHABET = BASE_ALPHABET.upper()


# Shoud letter frequency ('etaoinshrdlcumwfgypbvkjxqz') be used instead?
_ALPHA_CHARACTERS = BASE_ALPHABET + WORD_SEPARATOR + UPPER_ALPHABET
_ALPHA_MAP = {
  c: 2**i for i, c in enumerate(_ALPHA_CHARACTERS)
}
_ALPHA_MAP[UNIT_SEPARATOR] = _ALPHA_MAP[' ']


def normalize(string: str) -> str:
  return string.replace(UNIT_SEPARATOR, ' ')


def map_to_str(provide_mask: int, require_mask: int) -> str:
  chars = []
  for i in range(26):
    if require_mask and require_mask & (2 ** i):
      chars.append(chr(ord('A') + i))
    elif provide_mask and provide_mask & (2 ** i):
      chars.append(chr(ord('a') + i))
  return ''.join(chars)


def for_alpha(character: str) -> int:
  if len(character) != 1:
    raise ValueError('Only provide 1 character ("%s" given)' % character)
  if character in _ALPHA_MAP:
    return _ALPHA_MAP[character]
  raise NotImplementedError('Unable to compute mask for "%s"' % character)


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

  def __req__(self, other: int) -> bool:
    return True


PROVIDE_NOTHING = BitMatchAnything()
REQUIRE_NOTHING = BitMatchAnything()
