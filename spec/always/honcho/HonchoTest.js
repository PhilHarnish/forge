var spec = require("../../../test"),

    Honcho = require("always/honcho/Honcho.js"),
    fixtures = require("spec/revolver/fixtures");

describe("Watching directories", function () {
});

describe("Detect relationships", function () {
  var h;
  beforeEach(function () {
    h = new Honcho;
    h.addDeps(fixtures.getDeps());
  });

  it("should populate dependency data", function () {
    expect(h.getFiles().length).toBeGreaterThan(0);
  });

  it("should identify tests", function () {
    expect(h.getTests().length).toBeGreaterThan(0);
  });

  it("should detect complete and incomplete dependencies", function () {
    expect(h.isComplete()).toBeTruthy();
    h.addDeps({"missing_deps.js": ["non_existent_file.js"]});
    expect(h.isComplete()).toBeFalsy();
  });

  it("should detect system under test", function () {

  });
});
