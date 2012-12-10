var Fixture = require("./Fixture.js");

describe("Fixture", function () {
  var input = {
    "default": {
      "key": "default value"
    },
    "example": {
      "key": "example value"
    }
  };
  var fixture;
  beforeEach(function () {
    fixture = Fixture(input);
  });

  it("should get default fixtures", function () {
    expect(fixture.get()).toEqual(input["default"]);
  });

  it("should get named fixtures", function () {
    expect(fixture.get("example")).toEqual(input["example"]);
  });

  it("should get throw for missing fixtures", function () {
    expect(function () { fixture.get("missing") }).
        toThrow("Object #<Object> has no key 'missing'");
  });
});
