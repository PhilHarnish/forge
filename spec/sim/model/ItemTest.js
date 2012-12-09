var spec = require("../../../test");
var items = require("./fixtures/sim-items.js");

describe("Item", function() {
  beforeEach(register('sim/model/Item.js'));

  describe('Mocked requests', function () {
    beforeEach(items.mockRequests);
    afterEach(items.verifyRequests);

    it('should have an Item endpoint.', function(Item) {
      expect(Item.query).toBeTruthy();
    });

    it('should request IDs.', function(Item, $httpBackend) {
      items.expect("GET", items.request);
      var response = items.response;
      var resource = Item.query();
      expect(resource).toBeEmpty();
      $httpBackend.flush();
      expect(response.length).toEqual(resource.length);
      for (var i = 0; i < response.length; i++) {
        expect(resource).toHave(response);
      }
    });
  });
});
