var spec = require('../../test'),
    State = require('always/State.js');

describe('Construction', function () {
  it('should accept constructor arguments.', function () {
    var s = new State({tautology: true,
        contradiction: false});
    s.get('tautology').should.equal(true);
    s.get('contradiction').should.equal(false);
  });

  it('should set and get.', function () {
    var s = new State();
    expect(s.get('lost')).toBeUndefined();
    s.set('found', 'value').should.equal('value');
  });
});
