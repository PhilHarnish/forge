const string = require('../../src/util/string.js');
const alphabet = require('../../src/folding/alphabet.js');

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

  describe('rotate', () => {
    it('should be a no-op for 0 degrees', () => {
      expect(string.rotate('asdf', 0)).toEqual('asdf');
    });

    it('should rotate 1 character regardless of angle', () => {
      expect(string.rotate('a', 90)).toEqual('a');
      expect(string.rotate('a', 180)).toEqual('a');
      expect(string.rotate('a', 270)).toEqual('a');
    });

    it('should reverse 1 row after 180 degrees', () => {
      expect(string.rotate('rotate', 180)).toEqual('etator');
    });

    it('should rotate 1 row into 1 column', () => {
      expect(string.rotate('asdf', 90)).toEqual('a\ns\nd\nf');
    });

    describe('with transformations', () => {
      const ROTATIONS = [
        [
          'BWEM',
          'BWEM',
          'BWEM',
          'BWEM',
        ].join('\n'),
        [
          'WWWW',
          'EEEE',
          'MMMM',
          'BBBB',
        ].join('\n'),
        [
          'WBME',
          'WBME',
          'WBME',
          'WBME',
        ].join('\n'),
        [
          'EEEE',
          'WWWW',
          'BBBB',
          'MMMM',
        ].join('\n'),
      ];

      const ROTATION_MAPS = [
        string.mapAscii(alphabet.ALPHABET_MAX[0], alphabet.ALPHABET_MAX[0]),
        string.mapAscii(alphabet.ALPHABET_MAX[0], alphabet.ALPHABET_MAX[1]),
        string.mapAscii(alphabet.ALPHABET_MAX[0], alphabet.ALPHABET_MAX[2]),
        string.mapAscii(alphabet.ALPHABET_MAX[0], alphabet.ALPHABET_MAX[3]),
      ];

      it('should perform other rotations', () => {
        for (let i = 0; i < 4; i++) {
          let rotation = string.rotate(ROTATIONS[0], i * 90);
          let translated = string.translate(rotation, ROTATION_MAPS[i]);
          expect(translated).toEqual(ROTATIONS[i]);
        }
      });
    });
  });
});
