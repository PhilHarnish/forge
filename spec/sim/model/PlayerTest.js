var spec = require("../../../test");
var items = require("./fixtures/sim-items.js");
var players = require("./fixtures/sim-players.js");

describe("Player", function() {
  beforeEach(register("sim/model/Player.js"));

  it("should have an Player endpoint.", function(Player) {
    expect(Player).toHave("get");
  });

  describe("Mock requests", function () {
    beforeEach(items.mockRequests);
    beforeEach(players.mockRequests);
    afterEach(players.verifyRequests);

    it("should request IDs.", function(Player, $httpBackend) {
      var request = players.requests[0];
      var response = players.responses[0];
      players.expect("GET", request);
      var resource = Player.get({id: response._id.$oid});
      expect(resource).toBeEmpty();
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
        resource = Player.get({id: response._id.$oid});
        $httpBackend.flush();
      }));

      it("should be initialized.", function() {
        expect(resource.initialized()).toBeTruthy();
      });
    });
  });
});
