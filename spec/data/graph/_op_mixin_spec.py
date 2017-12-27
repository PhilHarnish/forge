from data.graph import _op_mixin
from spec.mamba import *


class Stub(_op_mixin.OpMixin):
  def _alloc(self, *args, **kwargs) -> 'Stub':
    return Stub(*args, **kwargs)


with description('construction'):
  with it('constructs without error'):
    expect(calling(_op_mixin.OpMixin)).not_to(raise_error)

  with it('constructs stub without error'):
    expect(calling(Stub)).not_to(raise_error)


with description('overloading'):
  with it('should begin with identity operation'):
    expect(str(Stub())).to(equal('Stub()'))

  with it('should accumulate with addition'):
    expect(str(Stub() + Stub())).to(equal('Stub((Stub()+Stub()))'))

  with it('should accumulate with multiplication'):
    expect(str(Stub() * Stub())).to(equal('Stub((Stub()*Stub()))'))

  with it('should accumulate with AND'):
    expect(str(Stub() & Stub())).to(equal('Stub((Stub()&Stub()))'))

  with it('should accumulate with OR'):
    expect(str(Stub() | Stub())).to(equal('Stub((Stub()|Stub()))'))

  with it('should support float with multiplication'):
    expect(str(Stub() * 0.5)).to(equal('Stub((Stub()*0.5))'))

  with it('should accumulate recursively'):
    a = Stub() + Stub()
    b = Stub() + Stub()
    expect(str(a * b)).to(
        equal('Stub((Stub((Stub()+Stub()))*Stub((Stub()+Stub()))))'))

  with it('should flatten commutative operations'):
    a = Stub() + Stub()
    b = Stub() + Stub()
    expect(str(a + b)).to(equal('Stub((Stub()+Stub()+Stub()+Stub()))'))
