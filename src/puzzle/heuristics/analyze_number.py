from puzzle.heuristics import acrostic

_BASE_HIGH_PRIORITY = [
  10, 16, 2, 26,
]
_BASE_PRIORITY = _BASE_HIGH_PRIORITY + [
  i for i in range(2, 40) if i not in _BASE_HIGH_PRIORITY
]
_HEURISTICS = []


def solutions(n):
  if not n:
    return
  for base in _BASE_PRIORITY:
    digits = _get_digits_in_base(n, base)
    min_digit = min(digits)
    max_digit = max(digits)
    for heuristic in _HEURISTICS:
      for result in heuristic(digits, min_digit, max_digit):
        yield result
  return


def _get_digits_in_base(n, b):
  digits = []
  while n:
    digits.append(int(n % b))
    n //= b
  return list(reversed(digits or [0]))


_HEX_ALPHABET = [
  'o',  # 0.
  'l',  # 1.
  'z',  # 2.
  'e',  # 3.
  'a',  # 4.
  's',  # 5.
  'b',  # 6.
  't',  # 7.
  'b',  # 8.
  '',  # 9.
  'a',  # A.
  'b',  # B.
  'c',  # C.
  'd',  # D.
  'e',  # E.
  'f',  # F.
]


def _hexspeak(digits, min_digit, max_digit):
  if max_digit > 15:
    return
  as_letters = []
  for digit in digits:
    letters = _HEX_ALPHABET[digit]
    if not letters:
      return
    as_letters.append(letters)
  for solution in acrostic.Acrostic(as_letters):
    yield solution, 1
  return


_HEURISTICS.append(_hexspeak)
