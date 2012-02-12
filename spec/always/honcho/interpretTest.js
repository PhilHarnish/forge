var spec = require("../../../test"),

    fixtures = require("spec/revolver/fixtures"),
    interpret = require("always/mother/interpret.js"),
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
    revolver.unload(["always/mother/interpret.js"]);
    interpret = require("always/mother/interpret.js");
  });

  it("should visit custom handler once", function () {
    var resource = {
      fileName: "example.txt",
      contents: ""
    };
    interpret.interpreter("text/plain", customInterpreter);
    expect(called).toBeFalsy();
    interpret.interpret(resource);
    expect(called).toBe(1);
    resource.fileName = "example.js";
    interpret.interpret(resource);
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
      var resource = {
        fileName: file,
        contents: ""
      };
      actual[file] = interpret.identify(resource).type;
    }
    expect(expected).toEqual(actual);
  });
});

describe("Interpretation", function () {
  var result;
  it("should return basic file information", function () {
    var resource = {
      fileName: "example.txt",
      contents: ""
    };
    result = interpret.interpret(resource);
    expect(result.fileName).toEqual("example.txt");
    expect(result.type.type).toEqual("text/plain");
  });
});
