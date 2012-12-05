var spec = require('../../../test');
var MongolabEndpoint = require('sim/model/MongolabEndpoint.js');

describe('MongolabEndpoint', function() {
  beforeEach(angular.mock.module('sim/db/MongolabEndpoint.js'));

  it('should resolve MongolabEndpoint factory.', function(MongolabEndpoint) {
    expect(MongolabEndpoint).toBeTruthy();
  });

  describe('Mocked requests', function () {
    var $httpBackend;
    var endpoint;
    var baseUrl;
    var request;
    var response = {user: 'id'};

    beforeEach(inject(function($injector, MongolabEndpoint) {
      baseUrl = MongolabEndpoint.BASE_URL + 'some-collection/';
      request = baseUrl + 'ID?apiKey=' + MongolabEndpoint.DEFAULTS.apiKey;
      $httpBackend = $injector.get('$httpBackend');
      $httpBackend.
          when('GET', request).
          respond(response);
      endpoint = MongolabEndpoint('some-collection/:id');
    }));

    afterEach(function() {
      $httpBackend.verifyNoOutstandingExpectation();
      $httpBackend.verifyNoOutstandingRequest();
    });

    it('should create a MongolabEndpoint.', function() {
      expect(endpoint.update).toBeTruthy();
    });

    it('should request IDs.', function() {
      $httpBackend.expectGET(request);
      var resource = endpoint.get({id: 'ID'});
      expect(resource).toBeEmpty();
      $httpBackend.flush();
      expect(resource).toHave(response);
    });
  });
});
