# Anagram another word.
import collections

ANAGRAM_INDICATORS = frozenset([
  'about',
  'awful',
  'bad',
  'badly',
  'break',
  'round',
  'crash',
  'crazy',
  'confuse',
  'destruction',
  'downfall',
  'from',
  'kink',
  'make',
  'mess',
  'odd',
  'oddly',
  'off',
  'out',
  'put',
  'roll',
  'round',
  'shake',
  'transform',
  'upset',
  'wander',
  'wandering',
])
# Solution appears in clue.
EMBEDDED_INDICATORS = frozenset([
  'bit',
  'circling',
  'in',
  'part',
  'partly',
])
# Synonym sounds like solution.
HOMOPHONE_INDICATORS = frozenset([
  'hear',
  'say',
])
# First letter.
INITIAL_INDICATORS = frozenset([
  'first',
  'initial',
  'initially',
  'lead',
])
# Join words.
CONCATENATE_INDICATORS = frozenset([
  'and',
  'by',
  'put',
  'with',
])
# Insert a word into another word.
INSERT_INDICATORS = frozenset([
  'stuck',
  'in',
])
# Front and back letters.
EDGES_INDICATORS = frozenset([
  'edge',
])
# Reversing words.
REVERSAL_INDICATORS = frozenset([
  'turn',
  'turning',
  'back',
  'backward',
])
# Ambiguous definition (e.g., double entendre).
AMBIGUOUS_INDICATORS = frozenset([
  '?'
])
# Shorthand conversions.
# TODO: This doesn't scale. Need a synonym list.
SHORTHAND_CONVERSIONS = {
  'american': ['us', 'usa'],
  'attempt': ['try'],
  'father': ['pa'],
  'fathers': ['pas'],
  'foot': ['ft'],
  'good': ['g'],
  'right': ['r'],
  'left': ['l'],
  'microphone': ['mic'],
}

ALL_INDICATORS = collections.defaultdict(list)
for group in [
  ANAGRAM_INDICATORS, EMBEDDED_INDICATORS, HOMOPHONE_INDICATORS,
  INITIAL_INDICATORS, CONCATENATE_INDICATORS, INSERT_INDICATORS,
  EDGES_INDICATORS, REVERSAL_INDICATORS,
]:
  for indicator in group:
    ALL_INDICATORS[indicator].append(group)
