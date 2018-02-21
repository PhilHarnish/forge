from data.graph import bloom_mask, bloom_node, edge_mask_iter_util
from spec.mamba import *

with description('iterable_both') as self:
  with before.each:
    self.a = bloom_node.BloomNode()
    self.a.open('a')  # Unique to a.
    self.a.open('c')  # Common.
    self.b = bloom_node.BloomNode()
    self.b.open('b')  # Unique to b.
    self.b.open('c')  # Common.

  with it('returns nothing for empty input'):
    expect(list(edge_mask_iter_util.iterable_both([]))).to(equal([]))

  with it('returns nothing for whitelist miss'):
    expect(list(edge_mask_iter_util.iterable_both(
        [self.a, self.b],
        whitelist=bloom_mask.for_alpha(' ')))).to(equal([]))

  with it('returns all items for single object'):
    expect(list(sorted(edge_mask_iter_util.iterable_both([self.a])))).to(equal([
      ('a', [self.a['a']]),
      ('c', [self.a['c']]),
    ]))

  with it('returns either items for multiple'):
    expect(list(sorted(edge_mask_iter_util.iterable_both(
        [self.a, self.b]
    )))).to(equal([
      ('a', [self.a['a']]),
      ('b', [self.b['b']]),
      ('c', [self.a['c'], self.b['c']]),
    ]))

  with it('optionally focuses specified items'):
    expect(list(edge_mask_iter_util.iterable_both(
        [self.a, self.b],
        whitelist=bloom_mask.for_alpha('b'),
    ))).to(equal([
      ('b', [self.b['b']]),
    ]))

  with it('optionally skips specified items'):
    expect(list(edge_mask_iter_util.iterable_both(
        [self.a, self.b],
        blacklist=bloom_mask.for_alpha('b'),
    ))).to(equal([
      ('a', [self.a['a']]),
      ('c', [self.a['c'], self.b['c']]),
    ]))

  with it('optionally skips and focuses specified items'):
    expect(list(edge_mask_iter_util.iterable_both(
        [self.a, self.b],
        whitelist=bloom_mask.for_alpha('a') | bloom_mask.for_alpha('b'),
        blacklist=bloom_mask.for_alpha('a'),
    ))).to(equal([
      ('b', [self.b['b']]),
    ]))


with description('iterable_common') as self:
  with before.each:
    self.a = bloom_node.BloomNode()
    self.a.open('a')  # Unique to a.
    self.a.open('c')  # Common.
    self.b = bloom_node.BloomNode()
    self.b.open('b')  # Unique to b.
    self.b.open('c')  # Common.

  with it('returns nothing for empty input'):
    expect(list(edge_mask_iter_util.iterable_common([]))).to(equal([]))

  with it('returns all items for single object'):
    expect(list(edge_mask_iter_util.iterable_common(
        [self.a]
    ))).to(equal([
      ('a', [self.a['a']]),
      ('c', [self.a['c']]),
    ]))

  with it('returns common items for multiple'):
    expect(list(edge_mask_iter_util.iterable_common(
        [self.a, self.b]
    ))).to(equal([
      ('c', [self.a['c'], self.b['c']]),
    ]))

  with it('optionally focuses specified items'):
    self.a.open('b')
    expect(list(edge_mask_iter_util.iterable_common(
        [self.a, self.b],
        whitelist=bloom_mask.for_alpha('b'),
    ))).to(equal([
      ('b', [self.a['b'], self.b['b']]),
    ]))

  with it('optionally skips specified items'):
    expect(list(edge_mask_iter_util.iterable_common(
        [self.a, self.b],
        blacklist=bloom_mask.for_alpha('c'),
    ))).to(equal([]))

  with it('optionally skips and focuses specified items'):
    self.a.open('b')
    expect(list(edge_mask_iter_util.iterable_common(
        [self.a, self.b],
        whitelist=bloom_mask.for_alpha('b') | bloom_mask.for_alpha('c'),
        blacklist=bloom_mask.for_alpha('c'),
    ))).to(equal([
      ('b', [self.a['b'], self.b['b']]),
    ]))
