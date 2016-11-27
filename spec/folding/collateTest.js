const collate = require('../../src/folding/collate.js');

describe('collate', () => {
  beforeEach(() => {
    collate.reset();
  });

  it('exports results', () => {
    expect(collate).toBeDefined();
    expect(collate.results).toBeDefined();
  });

  it('does not repeat work if already calculated', () => {
    spyOn(collate, 'add').and.callThrough();
    expect(collate.add).not.toHaveBeenCalled();
    collate.init();
    expect(collate.add).toHaveBeenCalled();
    const callsBefore = collate.add.calls.count();
    collate.init();  //
    const callsAfter = collate.add.calls.count();
    expect(callsBefore).toEqual(callsAfter);
  });

  describe('once initialized', () => {
    beforeEach(() => {
      collate.init();
    });

    const EXPECTED = [
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
    ];

    for (let i = 0; i < EXPECTED.length; i++) {
      let expected = Array.from(EXPECTED[i]).sort();
      it(`should find the specific solutions for ${i} tabs`, () => {
        let actual = Array.from(collate.results[i]).sort();
        expect(actual).toEqual(expected);
      });
    }
  });
});
