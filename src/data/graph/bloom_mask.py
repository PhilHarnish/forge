_ALPHA_CHARACTERS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
_ALPHA_MAP = {
  c: 2**i for i, c in enumerate(_ALPHA_CHARACTERS)
}


def for_alpha(character: str) -> int:
  if len(character) != 1:
    raise ValueError('Only provide 1 character ("%s" given)' % character)
  if character in _ALPHA_MAP:
    return _ALPHA_MAP[character]
  raise NotImplementedError('Unable to compute mask for "%s"' % character)
