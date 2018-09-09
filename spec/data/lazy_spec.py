from data import lazy
from spec.mamba import *


class TestClass(object):
  def __init__(self) -> None:
    self.n_calls = 0

  @lazy.prop
  def first(self) -> int:
    self.n_calls += 1
    return self.n_calls

  @lazy.prop
  def second(self) -> int:
    self.n_calls += 1
    return self.n_calls


with description('lazy'):
  with it('caches property'):
    c = TestClass()
    expect(c.first).to(equal(1))
    expect(c.first).to(equal(1))
    expect(c.n_calls).to(equal(1))

  with it('caches separately'):
    c = TestClass()
    expect(c.first).to(equal(1))
    expect(c.second).to(equal(2))
    expect(c.n_calls).to(equal(2))
