var spec = require("../../../test");
var items = require("./fixtures/sim-items.js");
var locations = require("./fixtures/sim-locations.js");
var players = require("./fixtures/sim-players.js");

describe("Player", function() {
  beforeEach(register("sim/model/Player.js"));

  describe("Mock requests", function () {
    beforeEach(items.mockRequests);
    beforeEach(locations.mockRequests);
    beforeEach(players.mockRequests);
    afterEach(players.verifyRequests);

    it("should request IDs.", function(Player, $httpBackend) {
      var request = players.requests[0];
      var response = players.responses[0];
      players.expect("GET", request);
      var resource = new Player(response._id.$oid);
      expect(resource.data).toBeEmpty();
      expect(resource.initialized()).toBeFalsy();
      $httpBackend.flush();
      expect(resource.initialized()).toBeTruthy();
    });

    describe("Mocked requests", function() {
      var resource;
      beforeEach(inject(function(Player, $httpBackend) {
        var request = players.requests[0];
        var response = players.responses[0];
        players.expect("GET", request);
        resource = new Player(response._id.$oid);
        $httpBackend.flush();
      }));

      it("should be initialized.", function() {
        expect(resource.initialized()).toBeTruthy();
      });
    });
  });
});
