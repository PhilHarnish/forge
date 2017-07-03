from data import operator_overloading
from spec.mamba import *


with description('operator_overloading'):
  with before.all:
    def overloaded(op, rop):
      def fn(self, other):
        return op(self.value, other)
      return fn
    @operator_overloading.overload_with_fn(overloaded)
    class Overloaded(object):
      def __init__(self, v):
        self.value = v
    self.Overloaded = Overloaded
    self.subject = Overloaded(5)

  with it('overloads cls <op> primitive'):
    actual = [
      self.subject + 1,
      1 + self.subject,
      self.subject - 1,
      1 - self.subject,
      self.subject > 1,
      1 > self.subject,
      self.subject >= 1,
      1 >= self.subject,
      self.subject < 1,
      1 < self.subject,
      self.subject <= 1,
      1 <= self.subject,
      self.subject == 1,
      1 == self.subject,
      self.subject != 1,
      1 != self.subject,
    ]

  with it('overloads cls <op> cls'):
    actual = [
      self.subject + self.Overloaded(1),
      self.Overloaded(1) + self.subject,
      self.subject - self.Overloaded(1),
      self.Overloaded(1) - self.subject,
      self.subject > self.Overloaded(1),
      self.Overloaded(1) > self.subject,
      self.subject >= self.Overloaded(1),
      self.Overloaded(1) >= self.subject,
      self.subject < self.Overloaded(1),
      self.Overloaded(1) < self.subject,
      self.subject <= self.Overloaded(1),
      self.Overloaded(1) <= self.subject,
      self.subject == self.Overloaded(1),
      self.Overloaded(1) == self.subject,
      self.subject != self.Overloaded(1),
      self.Overloaded(1) != self.subject,
    ]
    expect(actual).to(equal([
      6, 6,
      4, -4,
      True, False,
      True, False,
      False, True,
      False, True,
      False, False,
      True, True
    ]))
