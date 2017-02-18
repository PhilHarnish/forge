from src.origen import data
from src.origen import seven_segment


class WordList(list):

  def __init__(self, name, words):
    super(WordList, self).__init__(words)
    self.name = name


ALPHABET = data.load('data/seven_segment_alphabet.txt', seven_segment.Glyphs)
ACCESS_WORDS = data.load('data/seven_segment_access_words.txt', WordList)
