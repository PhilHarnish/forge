var spec = require("../../../test");
var status = require("spec/sim/model/fixtures/status.js");

describe("Status", function() {
  beforeEach(register("sim/ui/Status.js"));

  it("should be defined.", function(Status) {
    expect(Status).toBeDefined();
  });
});
