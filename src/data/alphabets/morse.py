from typing import List, Optional

ALPHABET = {
  'a': '.-',
  'b': '-...',
  'c': '-.-.',
  'd': '-..',
  'e': '.',
  'f': '..-.',
  'g': '--.',
  'h': '....',
  'i': '..',
  'j': '.---',
  'k': '-.-',
  'l': '.-..',
  'm': '--',
  'n': '-.',
  'o': '---',
  'p': '.--.',
  'q': '--.-',
  'r': '.-.',
  's': '...',
  't': '-',
  'u': '..-',
  'v': '...-',
  'w': '.--',
  'x': '-..-',
  'y': '-.--',
  'z': '--..',
  '0': '-----',
  '1': '.----',
  '2': '..---',
  '3': '...--',
  '4': '....-',
  '5': '.....',
  '6': '-....',
  '7': '--...',
  '8': '---..',
  '9': '----.',
}
LOOKUP = {v: k for k, v in ALPHABET.items()}

TRANSLATION_TABLES = [
  str.maketrans('012', ' .-'),
  str.maketrans('021', ' .-'),
  str.maketrans('201', ' .-'),
  str.maketrans('210', ' .-'),
]


def translate(code: str) -> Optional[List[str]]:
  parts = code.split(' ')
  result = []
  for part in parts:
    if part in LOOKUP:
      result.append(LOOKUP[part])
    else:
      return None
  return result
