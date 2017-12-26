from data import pool
from spec.mamba import *


class PoolStub(pool.Pooled):
  allocated = 0

  def __init__(self, value: int) -> None:
    super(PoolStub, self).__init__()
    self.value = value

  def _alloc(self) -> pool.Pooled:
    PoolStub.allocated += 1
    return PoolStub(0)

  def __str__(self) -> str:
    return 'PoolStub(%s)' % self.value


with description('construction'):
  with after.each:
    pool.reset()

  with it('constructs without error'):
    expect(calling(pool.Pooled)).not_to(raise_error)


with description('pooling'):
  with after.each:
    pool.reset()
    PoolStub.allocated = 0

  with it('should create new instances from instances'):
    a = PoolStub(1)
    b = a.alloc()
    expect(b).to(be_a(PoolStub))
    b.value = 2
    expect(str(a)).not_to(equal(str(b)))

  with it('should allocate new instances if needed'):
    a = PoolStub(1)
    for _ in range(10):
      temp = a.alloc()
      expect(temp).to(be_a(PoolStub))
    expect(PoolStub.allocated).to(equal(10))

  with it('should reuse freed instances, if available'):
    a = PoolStub(1)
    for x in range(10):
      temp = a.alloc()
      expect(temp).to(be_a(PoolStub))
      temp.free()
    expect(PoolStub.allocated).to(equal(1))
