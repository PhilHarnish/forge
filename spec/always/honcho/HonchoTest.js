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
    h.addFileName("events/Event.js");
    var reference = h.find("events/Event.js");
    console.log(h._index);
  });
});
