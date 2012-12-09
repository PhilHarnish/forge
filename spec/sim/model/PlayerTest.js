var spec = require("../../../test");
var players = require("./fixtures/sim-players.js").players;

describe("Player", function() {
  beforeEach(register("sim/model/Player.js"));

  it("should have an Player endpoint.", function(Player) {
    expect(Player).toHave("get");
  });

  describe("Mock requests", function () {
    var $httpBackend;
    var request;
    var response = players[0];

    beforeEach(inject(function($injector, MongolabEndpoint) {
      request = MongolabEndpoint.BASE_URL + "sim-players/" +
          response._id.$oid +
          "?apiKey=" + MongolabEndpoint.DEFAULTS.apiKey;
      $httpBackend = $injector.get("$httpBackend");
      $httpBackend.
          when("GET", request).
          respond(response);
    }));

    afterEach(function() {
      $httpBackend.verifyNoOutstandingExpectation();
      $httpBackend.verifyNoOutstandingRequest();
    });

    it("should request IDs.", function(Player) {
      $httpBackend.expectGET(request);
      var resource = Player.get({id: response._id.$oid});
      expect(resource).toBeEmpty();
      expect(resource.initialized()).toBeFalsy();
      $httpBackend.flush();
      expect(resource.initialized()).toBeTruthy();
    });

    describe("Mocked requests", function() {
      var resource;
      beforeEach(inject(function(Player) {
        $httpBackend.expectGET(request);
        resource = Player.get({id: response._id.$oid});
        $httpBackend.flush();
      }));

      it("should be initialized.", function() {
        expect(resource.initialized()).toBeTruthy();
      });
    });
  });
});
