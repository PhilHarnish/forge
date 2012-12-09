var spec = require("../../../test");
var locations = require("./fixtures/sim-locations.js").locations;

describe("Location", function() {
  beforeEach(register("sim/model/Location.js"));

  it("should have an Location endpoint.", function(Location) {
    expect(Location).toHave("query");
  });

  describe("Mock requests", function () {
    var $httpBackend;
    var request;
    var response = locations;

    beforeEach(inject(function($injector, MongolabEndpoint) {
      request = MongolabEndpoint.BASE_URL + "sim-locations" +
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

    it("should request IDs.", function(Location) {
      $httpBackend.expectGET(request);
      var resource = Location.query();
      expect(resource).toBeEmpty();
      $httpBackend.flush();
      expect(resource.length).toEqual(response.length);
      for (var i = 0; i < response.length; i++) {
        expect(resource).toHave(response);
      }
    });

    describe("Mocked requests", function() {
      var resources;
      beforeEach(inject(function(Location) {
        $httpBackend.expectGET(request);
        resources = Location.query();
        $httpBackend.flush();
      }));

      it("should calculate distance.", function(Location) {
        expect(resources.length).toBeGreaterThan(0);
        var resource = resources[0];
        var offsets = [
          {
            altitude: 0,
            distance: 0,
            rotation: 0
          },
          {
            x: 1,
            altitude: 0,
            distance: 1,
            rotation: Math.PI // <
          },
          {
            x: 1,
            y: 1,
            altitude: 0,
            distance: 2,
            rotation: (Math.PI / 4) * -3 // L
          },
          {
            y: -2,
            altitude: 0,
            distance: 2,
            rotation: Math.PI / 2 // ^
          }
        ];
        for (var deltas in offsets) {
          var delta = offsets[deltas];
          var source = {
            x: resource.x + (delta.x || 0),
            y: resource.y + (delta.y || 0),
            z: resource.z + (delta.z || 0)
          };
          var direction = resource.direction(source);
          expect(delta).toHave(direction);
        }
      });
    });
  });
});
