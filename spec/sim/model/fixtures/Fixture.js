/**
 * Given a collection name and values, returns fixtures for that collection.
 *
 * Exports helper methods and properties as well.
 *
 * @param name
 * @param values
 */
exports.exports = function (name, values) {
  var result;
  // Assign to "exports" to help IntelliJ find these definitions.
  exports = {
    /**
     * Calls $httpBackend.expect.
     * @param method
     * @param request
     */
    expect: function (method, request) {
      inject(function ($httpBackend) {
        $httpBackend.expect(method, request);
      });
    },
    /**
     * Exports all anticipated requests and their correct response.
     *
     * Example usage:
     * beforeEach(items.mockRequests);
     */
    mockRequests: function () {
      inject(function ($httpBackend, MongolabEndpoint) {
        var request = MongolabEndpoint.BASE_URL + 'sim-' + name +
            '/:id' +
            '?apiKey=' + MongolabEndpoint.DEFAULTS.apiKey;
        var queryRequest = request.replace("/:id", "");
        $httpBackend.
            when('GET', queryRequest).
            respond(values);

        result.request = queryRequest;
        result.response = values;
        // Prepare requests for get({id: ...}) queries.
        for (var i = 0; i < values.length; i++) {
          var value = values[i];
          var id = value._id.$oid;
          var getRequest = request.replace(":id", id);
          $httpBackend.
              when('GET', getRequest).
              respond(value);
          result.requests.push(getRequest);
          result.responses.push(value);
        }
      });
    },
    /**
     * Verifies only expected requests were initiated.
     *
     * Example usage:
     * afterEach(items.verifyRequests)
     */
    verifyRequests: function () {
      inject(function ($httpBackend) {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
      });
    },
    /**
     * Convenience property for testing. Set to last initialized request.
     */
    request: undefined,
    /**
     * Convenience property for testing. Set to last initialized response.
     */
    response: undefined,
    requests: [],
    responses: []
  };
  result = exports;
  return exports;
};
