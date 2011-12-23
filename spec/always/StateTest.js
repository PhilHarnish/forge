var spec = require("../../test"),
    State = require("always/State.js");

describe("Construction", function () {
  it("should accept constructor arguments.", function () {
    var s = new State("test", {tautology: true,
        contradiction: false});
    s.get("tautology").should.equal(true);
    s.get("contradiction").should.equal(false);
  });

  it("should set and get.", function () {
    var s = new State();
    expect(s.get("lost")).toBeUndefined();
    s.set("found", "value").should.equal("value");
  });
});

describe("toString()", function () {
  it("should serialize an empty State.", function () {
    var s = new State();
    s.toString().should.equal("{}");
  });

  it("should serialize a simple root State.", function () {
    var s = new State();
    s.set("key", "value");
    s.toString().should.equal(JSON.stringify({key: "value"}));
  });


  it("should serialize a root State with children.", function () {
    var s = new State();
    s.add("child", State, {key: "value"});
    s.toString().should.equal(JSON.stringify({child: {key: "value"}}));
  });

  it("should root a child State when serializing", function () {
    var root = new State();
    var child = root.add("child", State, {key: "value"});
    child.toString().should.equal(JSON.stringify({child: {key: "value"}}));
  });
});

describe("updating", function () {
  it("should overwrite updates to properties", function () {
  });
  it("should blend updates to children", function () {
  });
});
