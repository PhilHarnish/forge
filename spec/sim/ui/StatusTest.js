var spec = require("../../../test");
var status = require("spec/sim/model/fixtures/status.js");

describe("Status", function() {
  beforeEach(register("sim/ui/Status.js"));

  it("should be defined.", function($controller, $rootScope) {
    scope = $rootScope.$new();
    scope.stats = status;
    var status = $controller("Status", {
      "$scope": scope
    });
    expect(status).toBeDefined();
  });
});
