const Permute = require('../../../src/util/set/Permute.js');

describe('Permute', () => {
  it('exports Permute', () => {
    expect(Permute).toBeDefined();
  });

  it('should construct without errors', () => {
    expect(() => {new Permute([])}).not.toThrow();
  });

  describe('small sample', () => {
    let sample;

    beforeEach(() => {
      sample = new Permute(['A', 'B', 'C']);
    });

    it('should next() the first provided element', () => {
      expect(sample.next()).toEqual('A');
    });

    it('should next() the original input', () => {
      expect([
        sample.next(), sample.next(), sample.next()
      ]).toEqual(['A', 'B', 'C']);
    });

    it('should report hasNext until input is exhausted', () => {
      expect(sample.hasNext()).toEqual(true);
      sample.next();
      sample.next();
      sample.next();
      expect(sample.hasNext()).toEqual(false);
    });

    it('should throw once input is exhausted', () => {
      sample.next();
      sample.next();
      sample.next();
      expect(() => { sample.next() }).toThrow(jasmine.any(RangeError));
    });

    it('should not throw if advance is called', () => {
      expect(() => { sample.advance() }).not.toThrow();
    });

    it('should produce different permutation after advance', () => {
      const first = [sample.next(), sample.next(), sample.next()];
      sample.advance();
      const second = [sample.next(), sample.next(), sample.next()];
      expect(first).not.toEqual(second);
    });

    it('with 6 elements size is 6', () => {
      expect(sample.size).toEqual(6);
    });

    it('should report canAdvance until permutations are exhausted', () => {
      for (let i = 1; i < sample.size; i++) {
        expect(sample.canAdvance()).toEqual(true);
        sample.advance();
      }
      expect(sample.canAdvance()).toEqual(false);
    });

    it('advance should eventually throw', () => {
      for (let i = 1; i < sample.size; i++) {
        sample.advance();
      }
      expect(() => { sample.advance() }).toThrow(jasmine.any(RangeError));
    });

    it('should produce unique outputs', () => {
      const seen = [];
      seen.push([sample.next(), sample.next(), sample.next()].join(''));
      for (let i = 1; i < 6; i++) {
        sample.advance();
        seen.push([sample.next(), sample.next(), sample.next()].join(''));
      }
      expect(seen.sort()).toEqual([
        'ABC', 'ACB', 'BAC', 'BCA', 'CAB', 'CBA'
      ]);
    });

    it('should start over after reset', function() {
      const first = [sample.next(), sample.next(), sample.next()];
      sample.advance();
      sample.advance();
      sample.reset();
      const second = [sample.next(), sample.next(), sample.next()];
      expect(first).toEqual(second);
    });
  });
});
