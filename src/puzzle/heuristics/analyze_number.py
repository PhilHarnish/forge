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


def _run_length(digits, max_length):
  """Returns [digit, n_seen], ... for input digits."""
  active = [digits[0], 0]
  result = [active]
  for digit in digits:
    if digit == active[0]:
      active[1] += 1
      if active[1] > max_length:
        return []  # Invalid.
    else:
      active = [digit, 1]
      result.append(active)
  return result


# Heuristics.
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


def _phone_number(digits, min_digit, max_digit):
  n_digits = len(digits)
  if max_digit > 9:  # Not decimal.
    return
  elif n_digits not in (7, 10, 11):  # 1-XXX-YYY-ZZZZ.
    # Not a phone number.
    return
  elif n_digits == 7:  # YYY-ZZZZ.
    skip = 0
  elif n_digits == 10:  # XXX-YYY-ZZZZ.
    if digits[0:3] == [8, 0, 0]:
      skip = 3
    else:
      skip = 0
  elif digits[0] == 1:  # 1-XXX-YYY-ZZZZ.
    if digits[1:4] == [8, 0, 0]:
      skip = 4
    else:
      skip = 1
  else:  # >1 leading digit.
    return
  as_letters = []
  prefix = ''.join([str(i) for i in digits[0:skip]])
  for digit in digits[skip:]:
    if digit < 2:
      return
    as_letters.append(_T9_DICT[digit])
  for solution in acrostic.Acrostic(as_letters):
    yield prefix + solution, 1


def _t9(digits, min_digit, max_digit):
  if min_digit < 2:
    return
  if max_digit > 9:
    return
  as_letters = []
  for digit, length in _run_length(digits, 4):
    offset = length - 1  # 1 based -> 0 based.
    try:
      if length > len(_T9_DICT[digit]):
        return
      as_letters.append(_T9_DICT[digit][offset])
    except:
      print(digit, length)
      return
  if not as_letters:
    return
  for solution in acrostic.Acrostic(as_letters):
    yield solution, 1


# Install.
_HEURISTICS.extend([_hexspeak, _phone_number, _t9])

# Data.
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

_T9_DICT = [
  None,  # 0.
  None,  # 1.
  'abc',  # 2.
  'def',  # 3.
  'ghi',  # 4.
  'jkl',  # 5.
  'mno',  # 6.
  'pqrs',  # 7.
  'tuv',  # 8.
  'wxyz',  # 9.
]
