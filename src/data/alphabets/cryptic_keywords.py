# Anagram another word.
ANAGRAM_INDICATORS = frozenset([
  'about',
  'awful',
  'broken',
  'round',
  'crashing',
  'crazy',
  'kinked',
  'made from',
  'odd',
  'oddly',
  'off',
  'upset',
])
# Solution appears in clue.
EMBEDDED_INDICATORS = frozenset([
  'bit',
  'in',
  'part of',
])
# Synonym sounds like solution.
HOMOPHONE_INDICATORS = frozenset([
  'say',
])
# First letter.
INITIAL_INDICATORS = frozenset([
  'about',
  'first',
  'initially',
  'with',
])
# Insert a word into another word.
INSERT_INDICATORS = frozenset([
  'stuck in',
  'in',
])
# Front and back letters.
EDGES_INDICATORS = frozenset([
  'edges',
])
# Reversing words.
REVERSAL_INDICATORS = frozenset([
  'turning back'
])
# Truncating clues. ("microphone" -> "mic")
TRUNCATION_INDICATORS = frozenset([
  'short',
])
# Ambiguous definition (e.g., double entendre).
AMBIGUOUS_INDICATORS = frozenset([
  '?'
])
# Shorthand conversions.
SHORTHAND_CONVERSIONS = {
  'american': ['US', 'USA'],
  'foot': ['ft'],
}

ALL_INDICATORS = frozenset(
    ANAGRAM_INDICATORS | EMBEDDED_INDICATORS | HOMOPHONE_INDICATORS |
    INITIAL_INDICATORS | INSERT_INDICATORS | EDGES_INDICATORS |
    REVERSAL_INDICATORS | TRUNCATION_INDICATORS | AMBIGUOUS_INDICATORS
)
