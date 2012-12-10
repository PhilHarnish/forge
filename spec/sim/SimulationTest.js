var spec = require('../../test');
var items = require("./model/fixtures/sim-items.js");
var locations = require("./model/fixtures/sim-locations.js");
var players = require("./model/fixtures/sim-players.js");

describe('Simulation', function() {
  var simulation;
  var scope;
  beforeEach(register('sim/Simulation.js'));
  beforeEach(items.mockRequests);
  beforeEach(players.mockRequests);
  beforeEach(locations.mockRequests);
  afterEach(players.verifyRequests);

  beforeEach(inject(function ($rootScope, $httpBackend, Simulation,
      $location, Item, Location, MongolabEndpoint, Player, Status) {
    scope = $rootScope.$new();
    simulation = new Simulation(scope, $location, Item, Location,
        MongolabEndpoint, Player, Status);
    $httpBackend.flush();
  }));

  it('should resolve Simulation factory.', function(Simulation) {
    expect(Simulation).toBeTruthy();
  });

  it('should initialize "items"', function() {
    expect(scope.items.length).toBeGreaterThan(0);
  });

  it('should initialize "locations"', function() {
    expect(scope.locations.length).toBeGreaterThan(0);
  });

  it('should initialize "player"', function() {
    expect(scope.player.initialized()).toBeTruthy();
  });
});
