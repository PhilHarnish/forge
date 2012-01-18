var spec = require("../../../test"),

    fixtures = require("spec/revolver/fixtures"),
    interpret = require("always/honcho/interpret.js"),
    revolver = require("src/revolver/revolver.js");

describe("Custom identifiers and interpreters", function () {
  var called;
  var customInterpreter = function () {
    called++;
    return {};
  };

  beforeEach(function () {
    called = 0;
  });

  afterEach(function () {
    // Reload interpret.
    revolver.unload(["always/honcho/interpret.js"]);
    interpret = require("always/honcho/interpret.js");
  });

  it("should visit custom handler once", function () {
    interpret.interpreter("text/plain", customInterpreter);
    expect(called).toBeFalsy();
    interpret.source("example.txt", "");
    expect(called).toBe(1);
    interpret.source("example.js", "");
    expect(called).toBe(1);
  });

  describe("efficiently", function () {
  });
});

describe("Identification", function () {
  var deps,
      root;
  beforeEach(function () {
    deps = fixtures.getDeps();
  });

  it("should identify basic file types.", function () {
    var expected = {
      "example.js": "application/javascript",
      "example.css": "text/css",
      "example.txt": "text/plain",
      "bogus": "bogus"
    };
    var actual = {};
    for (var file in expected) {
      actual[file] = interpret.identify(file, "").type;
    }
    expect(expected).toEqual(actual);
  });
});

describe("Interpretation", function () {
  var result;
  it("should return basic file information", function () {
    result = interpret.source("example.txt", "");
    expect(result.digest).toEqual("da39a3ee5e6b4b0d3255bfef95601890afd80709");
    expect(result.type.type).toEqual("text/plain");
    expect(result.fileName).toEqual("example.txt");
  });
});
