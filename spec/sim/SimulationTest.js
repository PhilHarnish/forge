var spec = require("../../test");
var items = require("./model/fixtures/sim-items.js");
var locations = require("./model/fixtures/sim-locations.js");
var players = require("./model/fixtures/sim-players.js");

describe("Simulation", function() {
  var simulation;
  var scope;
  beforeEach(register("sim/Simulation.js"));
  beforeEach(items.mockRequests);
  beforeEach(players.mockRequests);
  beforeEach(locations.mockRequests);
  afterEach(players.verifyRequests);

  beforeEach(inject(function ($controller, $rootScope, $httpBackend) {
    scope = $rootScope.$new();
    simulation = $controller("Simulation", {
      "$scope": scope
    });
    $httpBackend.flush();
  }));

  it("should initialize 'items'", function() {
    expect(scope.player.inventory.items.length).toBeGreaterThan(0);
  });

  it("should initialize 'locations'", function() {
    expect(scope.player.travelLog.locations.length).toBeGreaterThan(0);
  });

  it("should initialize 'player'", function() {
    expect(scope.player.initialized()).toBeTruthy();
  });
});
