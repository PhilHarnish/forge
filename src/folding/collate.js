// Given 4 arms, shuffle tabs and return strings.

const Permute = require('../util/set/Permute.js');

/** @type {Array<string> */
const TABS = [
  'CABD',
  'IJLK',
  'NPOM',
  'HGEF',
];
const COUNT = TABS[0].length;
const OFFSETS = {
  'CABD': 0,
  'IJLK': 1,
  'NPOM': 2,
  'HGEF': 3,
};
const TOP_LEFT = new Set(['A', 'E', 'I', 'M']);

const permute = new Permute(TABS);

module.exports = {
  results: [
    new Set(),
    new Set([
      'ABDC', 'EFHG', 'IJLK', 'MNPO'
    ]),
    new Set([
      'ABDK', 'ABHC', 'ANPC', 'EFDG',
      'EFLK', 'ENHG', 'IJHG', 'IJLC',
      'INPO', 'MBDO', 'MFPO', 'MJLK',
    ]),
    new Set([
      'ANHC', 'EFDK', 'IJHC', 'INHG',
      'INPC', 'MBDK', 'MFDO', 'MFLK',
    ]),
    new Set(['INHC', 'MFDK']),
  ],

  reset() {
    permute.reset();
    for (let result of this.results) {
      result.clear();
    }
  },

  init() {
    // Skip work if already done.
    if (this.results[1].size) {
      return;
    }
    // Forward (clockwise).
    do {
      for (let offset = 0; offset < COUNT; offset++) {
        permute.seek(0);
        let tabsUsed = 0;
        let slicePosition = offset;
        let result = '';
        let src;
        let dest;
        let next = /** @type {string} */(permute.next());
        // Clockwise.
        do {
          tabsUsed++;
          result += next.slice(slicePosition, COUNT);
          if (!permute.hasNext()) {
            break;
          }
          last = next;
          next = /** @type {string} */(permute.next());
          [src, dest] = [last, next];
          slicePosition = (4 - (OFFSETS[dest] - OFFSETS[src])) % 4;
        } while (result.length < COUNT);
        // Always add the last 4.
        this.add(result.slice(-COUNT), tabsUsed);
        // Counterclockwise.
        permute.seek(0);
        tabsUsed = 0;
        slicePosition = offset;
        result = '';
        next = /** @type {string} */(permute.next());
        do {
          tabsUsed++;
          result = next.slice(0, 4 - slicePosition) + result;
          if (!permute.hasNext()) {
            break;
          }
          last = next;
          next = /** @type {string} */(permute.next());
          [src, dest] = [last, next];
          slicePosition = (4 + (OFFSETS[dest] - OFFSETS[src])) % 4;
        } while (result.length < COUNT);
        // Always add the first 4.
        this.add(result.slice(0, COUNT), tabsUsed);
      }
    } while (permute.advance());
    // Fix mistakes. 3 tabs can be used to make 2-tab results.
    for (let result of this.results[2]) {
      this.results[3].delete(result);
    }
  },

  add(fold, numberOfTabs) {
    this.results[numberOfTabs].add(this.orient(fold));
  },

  orient(fold) {
    // Re-orient so that sequence starts with top-left letter.
    for (let i = 0; i < fold.length; i++) {
      if (TOP_LEFT.has(fold[i])) {
        return fold.slice(i, fold.length) + fold.slice(0, i);
      }
    }
  }
};
