from data import max_heap
from spec.mamba import *

with description(max_heap.MaxHeap):
  with description('push'):
    with it('accepts any inputs'):
      expect(calling(self.subject.push, 0, True)).not_to(raise_error)
      expect(calling(self.subject.push, 0, 1)).not_to(raise_error)
      expect(calling(self.subject.push, 0, 'data')).not_to(raise_error)

  with description('pop'):
    with it('raises for empty input'):
      expect(calling(self.subject.pop)).to(raise_error)

    with it('returns largest value'):
      self.subject.push(1, 'data')
      self.subject.push(0, 'irrelevant')
      expect(self.subject.pop()).to(equal('data'))

  with description('length'):
    with it('0 for empty'):
      expect(self.subject).to(have_len(0))

    with it('grows with push'):
      self.subject.push(0, 'data 1')
      expect(self.subject).to(have_len(1))
      self.subject.push(0, 'data 2')
      expect(self.subject).to(have_len(2))

  with description('best_weight'):
    with it('raises for empty input'):
      expect(calling(self.subject.best_weight)).to(raise_error)

    with it('returns the magnitude of largest value'):
      self.subject.push(1, 'small')
      self.subject.push(100, 'largest')
      self.subject.push(0, 'smallest')
      self.subject.push(10, 'large')
      expect(self.subject.best_weight()).to(equal(100))
