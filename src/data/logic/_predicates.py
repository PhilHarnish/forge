class Predicates(list):
  def __init__(self, values):
    super(Predicates, self).__init__(values)

  def __eq__(self, other):
    return Predicates([child == other for child in self])

  def __ne__(self, other):
    return Predicates([child != other for child in self])

  def __add__(self, other):
    return Predicates([child + other for child in self])

  def __sub__(self, other):
    return Predicates([child - other for child in self])

  def __lt__(self, other):
    return Predicates([child < other for child in self])

  def __le__(self, other):
    return Predicates([child <= other for child in self])

  def __gt__(self, other):
    return Predicates([child > other for child in self])

  def __ge__(self, other):
    return Predicates([child >= other for child in self])
