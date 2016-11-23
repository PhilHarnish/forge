const generators = require('../../src/util/generators.js');

describe('generators', () => {
  it('exports generators', () => {
    expect(generators).toBeDefined();
  });

  describe('range', () => {
    it('should return empty array for 0 length range', () => {
      expect(generators.range(0, 0)).toEqual([]);
    });

    it('should throw error for invalid input', () => {
      expect(() => { generators.range(9, 0)}).toThrow(jasmine.any(RangeError));
      expect(() => { generators.range(0, 1, 0)}).toThrow(
          jasmine.any(RangeError));
    });

    it('should produce simple arrays', () => {
      expect(generators.range(0, 3)).toEqual([0, 1, 2]);
    })
  });
});
