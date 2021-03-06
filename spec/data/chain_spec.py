from data import chain
from spec.mamba import *

with description('Chain'):
  with it('instantiates empty chain'):
    expect(chain.Chain(0)).to(have_len(0))

  with it('instantiates small chains'):
    expect(chain.Chain(1)).to(have_len(1))
    expect(chain.Chain(2)).to(have_len(2))

  with it('overrides iterator'):
    expected = list(['a', 'b', 'c', 'd'])
    actual = chain.Chain(['a', 'b', 'c', 'd'])
    for expected, actual in zip(expected, actual):
      expect(expected).to(equal(actual))

  with description('with mutations'):
    with before.each:
      self.subject = chain.Chain(5)

    with it('starts an iterable sequence'):
      expect(next(iter(self.subject))).to(equal(0))

    with it('exhausts an iterable sequence'):
      expect(list(self.subject)).to(equal([0, 1, 2, 3, 4]))

    with it('removes elements from middle'):
      self.subject.pop(1)
      self.subject.pop(3)
      expect(list(self.subject)).to(equal([0, 2, 4]))

    with it('removes elements from ends'):
      self.subject.pop(0)
      self.subject.pop(4)
      expect(list(self.subject)).to(equal([1, 2, 3]))

    with it('prevents removing redundantly'):
      while self.subject:
        self.subject.pop()
      expect(calling(self.subject.pop, 0)).to(raise_error(IndexError))

    with it('pops and restores'):
      self.subject.pop(1)
      self.subject.pop(3)
      expect(list(self.subject)).to(equal([0, 2, 4]))
      self.subject.restore(3)
      expect(list(self.subject)).to(equal([0, 2, 3, 4]))

    with it('long sequence of mutations replicates a sorted set'):
      active = {0, 1, 2, 3, 4}
      sequence = [
        0, 1, 2, 3, 4,  # Empty.
        '+', 4,  # Add & remove.
        '+', '+', '+', '+',  # 4, 3, 2, 1 restored.
        1, 3, 4,  # 2.
        '+', '+',  # 2, 3, 4.
      ]
      last_popped = []
      for instruction in sequence:
        if instruction == '+':
          i = last_popped.pop()
          expect(active).not_to(contain(i))
          self.subject.restore(i)
          active.add(i)
        else:
          i = instruction
          expect(active).to(contain(i))
          last_popped.append(i)
          self.subject.pop(i)
          active.remove(i)
        expect(list(self.subject)).to(equal(sorted(list(active))))
      expect(list(self.subject)).to(equal([2, 3, 4]))

  with description('with data'):
    with before.each:
      self.subject = chain.Chain('the quick brown fox jumped'.split())

    with it('provides data items()'):
      expect(list(self.subject.items())).to(equal([
        (0, 'the'), (1, 'quick'), (2, 'brown'), (3, 'fox'), (4, 'jumped'),
      ]))

    with it('deletes items and provides new results'):
      self.subject.pop(1)
      self.subject.pop(4)
      expect(list(self.subject.items())).to(equal([
        (0, 'the'), (2, 'brown'), (3, 'fox'),
      ]))
