var spec = require("../../../test");
var MongolabEndpoint = require('sim/model/MongolabEndpoint.js');
var Item = require("sim/model/Item.js");

describe("Item", function() {
  beforeEach(angular.mock.module('sim/db/Item.js'));

  describe('Mocked requests', function () {
    var $httpBackend;
    var request;
    var response = [{name: 'item'}];

    beforeEach(inject(function($injector, MongolabEndpoint) {
      request = MongolabEndpoint.BASE_URL + 'sim-items' +
          '?apiKey=' + MongolabEndpoint.DEFAULTS.apiKey;
      $httpBackend = $injector.get('$httpBackend');
      $httpBackend.
          when('GET', request).
          respond(response);
    }));

    afterEach(function() {
      $httpBackend.verifyNoOutstandingExpectation();
      $httpBackend.verifyNoOutstandingRequest();
    });

    it('should have an Item endpoint.', function(Item) {
      expect(Item.query).toBeTruthy();
    });

    it('should request IDs.', function(Item) {
      $httpBackend.expectGET(request);
      var resource = Item.query();
      expect(resource).toBeEmpty();
      $httpBackend.flush();
      expect(resource.length).toEqual(response.length);
      for (var i = 0; i < response.length; i++) {
        expect(resource).toHave(response);
      }
    });
  });
});
