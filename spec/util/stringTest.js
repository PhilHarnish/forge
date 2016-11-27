const string = require('../../src/util/string.js');

describe('string', () => {
  it('exports string', () => {
    expect(string).toBeDefined();
  });

  describe('mapAscii', () => {
    it('should return same result for no-ops', () => {
      const before = string.mapAscii('', '');
      const after = string.mapAscii('', '');
      expect(before).toEqual(after);
    });

    it('should return different results given input', () => {
      const before = string.mapAscii('b', 'a');
      const after = string.mapAscii('a', 'b');
      expect(before).not.toEqual(after);
    });
  });

  describe('translate', () => {
    const NO_OP = string.mapAscii('', '');
    const LEET = string.mapAscii('let', '137');

    it('should be a no-op for empty strings', () => {
      expect(string.translate('', NO_OP)).toEqual('');
    });

    it('should be a no-op for empty translations', () => {
      expect(string.translate('example', NO_OP)).toEqual('example');
    });

    it('should translate characters', () => {
      expect(string.translate('leet', LEET)).toEqual('1337');
    });
  });
});
