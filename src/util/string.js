const generators = require('./generators.js');

/** @const {string} 128 letter string where 0 = \0, 1 = \1 ... 65 = A, etc. */
const INITIAL_ASCII_MAP_ = String.fromCharCode.apply(
    null, generators.range(0, 128));

module.exports = {
  /**
   * Intended for use with translate().
   * @param {string} before Source characters to convert to `after`.
   * @param {string} after Characters converted from `before`.
   */
  mapAscii(before, after) {
    let result = INITIAL_ASCII_MAP_.split('');
    for (let i = 0; i < before.length; i++) {
      result[before.charCodeAt(i)] = after[i];
    }
    return result.join('');
  },

  translate(source, map) {
    let result = source.split('');
    let i = result.length;
    while (i--) {
      result[i] = map[source.charCodeAt(i)];
    }
    return result.join('');
  },

  rotate(source, degrees) {
    let result = source.split('\n');
    let rotated;
    while (degrees > 0) {
      rotated = [];
      degrees -= 90;
      for (let column = 0; column < result[0].length; column++) {
        const line = [];
        for (let row = result.length - 1; row >= 0; row--) {
          line.push(result[row][column]);
        }
        rotated.push(line.join(''));
      }
      result = rotated;
    }
    return result.join('\n');
  },
};
