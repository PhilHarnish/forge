var spec = require("../../../../test"),

    fixtures = require("spec/revolver/fixtures"),
    identifyJavaScript = require("src/always/mother/identifiers/" +
        "identifyJavaScript.js")["application/javascript"];

describe("Identifies attributes", function () {
  var type;
  beforeEach(function () {
    type = "application/javascript";
  });

  it("should identify NodeJS", function () {
    var fileName = "events/EventDispatcher.js";
    var result = identifyJavaScript(fileName,
        fixtures.getFileContents(fileName), type);
    expect(result).toEqual("application/javascript;nodejs=1");
  });

  it("should identify NodeJS tests.", function () {
    var fileName = "tests/events/EventDispatcherTest.js";
    var result = identifyJavaScript(fileName,
        fixtures.getFileContents(fileName), type);
    expect(result).toEqual("application/javascript;nodejs=1;test=1");
  });
});
