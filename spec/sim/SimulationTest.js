var spec = require('../../test');

describe('Simulation', function() {
  beforeEach(register('sim/Simulation.js'));

  it('should resolve MongolabEndpoint factory.', function(Simulation) {
    expect(Simulation).toBeTruthy();
  });

  it('should initialize "message"', function(Simulation) {
    var mockScope = {};
    var s = new Simulation(mockScope);
    expect(mockScope.message).toBe("Hello world.");
  });
});
