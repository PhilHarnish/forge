import collections
import math

from data.alphabets import braille, keyboard_intersection, leet, morse, t9
from puzzle.heuristics import acrostic

_BASE_HIGH_PRIORITY = [
  10, 16, 26, 36, 32, 2,
  128, 256,  # These extra bases are included for potential ASCII matches.
]
_BASE_PRIORITY = _BASE_HIGH_PRIORITY + [
  i for i in range(2, 40) if i not in _BASE_HIGH_PRIORITY
]
_HEURISTICS = []  # Updated at end.


def solutions(n):
  if not n:
    return
  for solution, notes in solutions_with_notes(n):
    yield solution


def solutions_with_notes(n):
  for base in _BASE_PRIORITY:
    for digits, notes in _get_digits_in_base(n, base):
      min_digit = min(digits)
      max_digit = max(digits)
      for heuristic in _HEURISTICS:
        for result in heuristic(digits, min_digit, max_digit):
          yield result, notes


def _solutions_for_letters(letters):
  l = len(letters)
  if l > 8:
    freq = collections.Counter(letters)
    letter, count = freq.most_common(1)[0]
    if letter in 'aeiou':
      if count > l / 2:
        return
    elif count ** 2 > l / 2:
      return
  for solution in acrostic.Acrostic(letters).items():
    yield solution


def _get_digits_in_base(n, b):
  """Converts and yields n in base b.

  Also yields if:
  - A pattern of spacer digits are discovered then another yield occurs with
    spacers removed.
  - TODO: A null digit (0) might be used to separate words.
  """
  digits = []
  notes = ['base%s' % b]
  # Look for patterns while converting base. For each digit, record when it was
  # first seen and, upon seeing it again the spacing between digits. If the
  # spacing pattern is violated the digit is stored as (None, None).
  patterns = {}
  pos = 0
  while n:
    digit = int(n % b)
    digits.append(digit)
    n //= b
    if digit in patterns:
      first, spacing = patterns[digit]
      if first is None:
        pass  # No pattern.
      elif spacing is None:
        spacing = pos - first
        if spacing == 1:  # This would remove everything.
          patterns[digit] = (None, None)
        elif spacing <= first:  # We first encountered this number too late
          patterns[digit] = (None, None)
        else:
          patterns[digit] = (first, spacing)
      elif (pos - first) % spacing:
        patterns[digit] = (None, None)  # Uneven spacing discovered.
    else:  # First occurrence.
      patterns[digit] = (pos, None)
    pos += 1
  result = list(reversed(digits or [0]))
  yield result, notes
  # Remove digits if there was a pattern.
  if b == 2 or len(patterns) == 2:
    return  # This is pointless when binary or there are only 2 digits.
  l = len(result)
  if l <= 10:
    return  # Sequence too small.
  for target, (first, spacing) in patterns.items():
    if first is None or spacing is None:
      continue
    if l // spacing <= 5:
      continue  # Removing just a few spacers isn't interesting.
    filtered = []
    # Need to adjust `first` because it was calculated pre-reversal.
    first = (l - first) % spacing - 1
    for i, digit in enumerate(result):
      if (i - first) % spacing:  # Not the pattern we're tracking.
        filtered.append(digit)
      elif digit != target:
        # This pattern didn't reach the end of the sequence.
        break
    else:  # End of for loop reached.
      note = 'filtered %s (+%s%s%s)' % (target, first, '%', spacing)
      yield filtered, notes + [note]


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
def _alphabet(digits, min_digit, max_digit):
  if min_digit == 0:
    return
  if max_digit > 26:
    return
  as_letters = []
  offset = ord('a') - 1
  for digit in digits:
    as_letters.append(chr(offset + digit))
  for solution in _solutions_for_letters(as_letters):
    yield solution


def _ascii(digits, min_digit, max_digit):
  if not chr(min_digit).isprintable():
    return
  elif not chr(max_digit).isprintable():
    return
  as_letters = []
  for digit in digits:
    letter = chr(digit)
    if not letter.isprintable():
      return
    as_letters.append(letter)
  solutions = set()
  for solution in _solutions_for_letters(as_letters):
    solutions.add(solution)
    yield solution
  if len(as_letters) < 10:
    return
  # If we got this far we're going to return a result. It's fairly improbable
  # for 10+ ASCII printable digits to be generated. The printable range of ASCII
  # is pretty spotty. However, the input may have been obfuscated-but-printable
  # ascii or simply contains punctuation. If so, return it as a low-weighted
  # result.
  printable_result = ''.join(as_letters)
  if printable_result not in solutions:
    yield printable_result, 0.25


def _ascii_nibbles(digits, min_digit, max_digit):
  num_digits = len(digits)
  if min_digit >= 16:
    return
  elif max_digit > 16:  # NB: Galactic included 16 as a delimiter.
    return
  elif num_digits < 2:
    return  # Takes 2 digits to make 1 letter.
  elif max_digit == 16:
    # Verify every 3rd digit is a delimiter.
    for i in range(2, num_digits, 3):
      if digits[i] != 16:
        return
    step = 3
  else:
    step = 2
    # Verify digits is an even number.
    if num_digits % 2:
      return
  as_letters = []
  for digit in range(0, num_digits, step):
    left, right = digits[digit], digits[digit + 1]
    if left == 16 or right == 16:
      return
    c = chr(left << 4 | right)
    if not c.isalpha():
      return
    as_letters.append(c.lower())
  for solution in _solutions_for_letters(as_letters):
    yield solution


def _base_n(digits, min_digit, max_digit):
  """Convert digits to letters assuming baseN (eg hex has A-F)."""
  if min_digit < 10:
    return
  if max_digit > 36:
    return
  offset = ord('a') - 10  # Assume 0-9 are reserved for digits.
  as_letters = []
  for digit in digits:
    as_letters.append(chr(digit + offset))
  for solution in _solutions_for_letters(as_letters):
    yield solution


def _braille(digits, min_digit, max_digit):
  """Braille.
  
  Increasing sequences of 1..6 specify raised dots (in column-major order, as
  standard for Braille), separated by 0s.
  """
  del min_digit
  if max_digit > 6:
    return
  elif digits[0] == 0:
    return
  as_letters = []
  acc = 0
  last = 0
  for digit in digits + [0]:
    if digit == 0:
      if braille.BITFIELD_ALPHABET[acc] is None:
        # Found an invalid character.
        return
      as_letters.append(braille.BITFIELD_ALPHABET[acc])
      acc = 0
    elif digit <= last:
      # Digits must always increase.
      return
    else:
      acc |= 1 << (digit - 1)
    last = digit
  for solution in _solutions_for_letters(as_letters):
    yield solution


def _hexspeak(digits, min_digit, max_digit):
  del min_digit
  if max_digit > 15:
    return
  as_letters = []
  for digit in digits:
    letters = leet.HEX_ALPHABET[digit]
    if not letters:
      return
    as_letters.append(letters)
  for solution in _solutions_for_letters(as_letters):
    yield solution


def _keyboard_intersection(digits, min_digit, max_digit):
  del min_digit, max_digit
  if len(digits) % 2 != 0:
    return
  as_letters = []
  for i in range(0, len(digits), 2):
    left, right = digits[i], digits[i + 1]
    key = str(left) + str(right)
    if key not in keyboard_intersection.LOOKUP:
      return
    as_letters.append(keyboard_intersection.LOOKUP[key])
  for solution in _solutions_for_letters(as_letters):
    yield solution


def _lexicographical_ordering(digits, min_digit, max_digit):
  if min_digit != 0:
    return
  elif max_digit > 5:
    # Number of lexographic orderings for 0..5 is already quite high.
    return
  # Read out numbers in batches of (max_digit-1).
  chunk_size = max_digit + 1
  if len(digits) % chunk_size != 0:
    # Should be possible to chunk digits into max_digit chunks.
    return
  as_letters = []
  offset = ord('a')
  for i in range(0, len(digits), chunk_size):
    remaining = list(range(chunk_size))  # Create a list of [0..max_digit)...
    acc = 0
    for j in range(chunk_size):  # ...and start extracting.
      cursor = digits[i + j]
      if cursor not in remaining:
        # Sequence is invalid. We've encountered a duplicate digit.
        return
      position = remaining.index(cursor)
      # When 3/3 are left, a leading 2 is 2*1 into the sequence.
      acc += position * math.factorial(len(remaining) - 1)
      remaining.pop(position)
    as_letters.append(chr(acc + offset))
  for solution in _solutions_for_letters(as_letters):
    yield solution


def _morse(digits, min_digit, max_digit):
  """Use 0, 1, 2 for morse. Sadly, there is no universal standard."""
  del min_digit
  if max_digit > 2:
    return
  word = ''.join([str(i) for i in digits])
  for translation in morse.TRANSLATION_TABLES:
    translated = morse.translate(word.translate(translation))
    if translated is None:
      continue
    for solution in _solutions_for_letters(translated):
      yield solution


def _phone_number(digits, min_digit, max_digit):
  del min_digit
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
    as_letters.append(t9.KEYS[digit])
  for word, score in _solutions_for_letters(as_letters):
    yield prefix + word, score


def _positional(digits, min_digit, max_digit):
  del min_digit
  if len(digits) != 26:
    return
  if max_digit > 10:
    return
  word_map = {}
  offset = ord('a')
  for i, digit in enumerate(digits):
    if not digit:
      continue
    if digit in word_map:
      return
    word_map[digit] = chr(i + offset)
  as_letters = []
  cursor = 1
  while cursor in word_map:
    as_letters.append(word_map[cursor])
    del word_map[cursor]
    cursor += 1
  if word_map:
    return  # Not all letters were used.
  for solution in _solutions_for_letters(as_letters):
    yield solution


def _runlength(digits, min_digit, max_digit):
  del min_digit, max_digit
  chunks = _run_length(digits, 26)
  if len(chunks) < 3:
    return
  # Determine if this is delimited.
  if len(chunks) > 3:
    step = 2  # Assume it is.
    delimiter = chunks[1][0]
    for i in range(1, len(chunks), 2):
      digit, length = chunks[i]
      if length == 1 and digit != delimiter:
        step = 1  # Verified not delimited.
        break
  else:
    step = 1
  longest = 0
  offset = ord('a') - 1
  as_letters = []
  for i in range(0, len(chunks), step):
    digit, length = chunks[i]
    longest = max(longest, length)
    as_letters.append(chr(offset + length))
  if len(as_letters) < 3 or longest < 10:
    return
  for solution in _solutions_for_letters(as_letters):
    yield solution


def _t9(digits, min_digit, max_digit):
  """Presses on phone keypad."""
  if min_digit < 2:
    return
  if max_digit > 9:
    return
  as_letters = []
  for digit, length in _run_length(digits, 4):
    offset = length - 1  # 1 based -> 0 based.
    try:
      if length > len(t9.KEYS[digit]):
        return
      as_letters.append(t9.KEYS[digit][offset])
    except:
      return
  if not as_letters:
    return
  for solution in _solutions_for_letters(as_letters):
    yield solution


# Install.
_HEURISTICS.extend([
  _alphabet, _ascii, _ascii_nibbles, _base_n, _braille, _hexspeak,
  _keyboard_intersection, _lexicographical_ordering, _morse, _phone_number,
  _positional, _runlength, _t9,
])
