import functools

from data import word_frequencies

@functools.lru_cache()
def letters():
  """All alphabet characters and their frequencies."""
  return word_frequencies.load(_LETTERS)


@functools.lru_cache()
def ambiguous():
  """A set of words which, when combined, form numerous ambiguous sentences."""
  return word_frequencies.load(_AMBIGUOUS_DATA)


@functools.lru_cache()
def everything():
  """This should only be used during prototyping. Very slow."""
  return word_frequencies.load_from_file('data/count_1w.txt')


_LETTERS = list(zip('abcdefghijklmnopqrstuvwxyz', [
  9081174698, 419765694, 596623239, 361493758, 593086170, 297285731,  # abcdef.
  227771642, 220523502, 3086225277, 180739802, 195647953, 252900442,  # ghijkl.
  341583838, 437961375, 246429812, 303249898, 139563801, 323534251,  # mnopqr.
  565123981, 388448018, 179615587, 204486977, 252231566, 508609523,  # stuvwx.
  195011703, 132095202,  # yz.
]))


# superbowlwarplanesnapshotscrapbookisnowhere
_AMBIGUOUS_DATA = [
  ('superbowl', 1599172),
  ('super', 66703287), ('bowl', 22118861), ('bowls', 4193933),
  ('superb', 7886083), ('owl', 5010726), ('owls', 2208765),
  ('warplane', 43421), ('warplanes', 158676),
  ('war', 126517399), ('plane', 17799728),
  ('warp', 2399276), ('lane', 24880931),
  ('snapshot', 7254276), ('snapshots', 2278001),
  ('snap', 7978122), ('shot', 41614412), ('shots', 19611119),
  ('snaps', 1512455), ('hot', 159287179), ('hots', 229153),
  ('nap', 2473014), ('naps', 496868),
  ('scrapbook', 3394030),
  ('scrap', 3757085), ('book', 330959949),
  ('crap', 7169097),
  ('boo', 2884230), ('kis', 356717),
  ('is', 4705743816),
  ('nowhere', 5582367),
  ('now', 611387736), ('here', 639711198),
] + _LETTERS
