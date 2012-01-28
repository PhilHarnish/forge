var spec = require("../../../test"),

    Honcho = require("always/honcho/Honcho.js"),
    fixtures = require("spec/revolver/fixtures");

describe("Watching directories", function () {
});

describe("Detect relationships", function () {
  var h;
  beforeEach(function () {
    h = new Honcho;
    h._getFileContents = fixtures.getFileContents;
  });

  it("should add a file", function () {
    h.load("events/Event.js");
    var resource = h.find("events/Event.js");
    expect(resource).toBeDefined();
  });

  it("should add all files", function () {
    for (var file in fixtures.getDeps()) {
      h.load(file);
    }
    // TODO: What asserts make sense? Nothing blew up, does that count?
    expect(true).toBeTruthy();
  });
});
