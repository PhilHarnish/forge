exports.exports = function (name, values) {
  var result;
  // Assign to "exports" to help IntelliJ find these definitions.
  exports = {
    expect: function (method, request) {
      inject(function ($httpBackend) {
        $httpBackend.expect(method, request);
      });
    },
    mockRequests: function () {
      inject(function ($httpBackend, MongolabEndpoint) {
        var request = MongolabEndpoint.BASE_URL + 'sim-' + name +
            '?apiKey=' + MongolabEndpoint.DEFAULTS.apiKey;
        $httpBackend.
            when('GET', request).
            respond(values);

        result.request = request;
      });
    },
    verifyRequests: function () {
      inject(function ($httpBackend) {
        $httpBackend.verifyNoOutstandingExpectation();
        $httpBackend.verifyNoOutstandingRequest();
      });
    },
    request: undefined,
    response: values
  };
  result = exports;
  return exports;
};
