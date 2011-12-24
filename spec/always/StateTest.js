var spec = require("../../test"),
    State = require("always/State.js");

var SubState = function (path, data) {
  State.call(this, path, data);
};
SubState.prototype = new State();

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

  it("should allow creation of children.", function () {
    var s = new State();
    var child = s.add("child");
    s.get("child").should.equal(child);
  });

  it("should allow specifying type of children.", function () {
    var s = new State();
    expect(SubState).toBeDefined();
    var a = s.group("a", SubState);
    expect(a.add("a1", {key: "value"})).toEqual(jasmine.any(State));
    expect(a.add("a2", {key: "value"})).toEqual(jasmine.any(SubState));
    var b = s.group("b", State);
    expect(b.add("b1", {key: "value"})).toEqual(jasmine.any(State));
    expect(b.add("b2", {key: "value"})).toNotEqual(jasmine.any(SubState));
    var c = s.group("c");
    expect(c.add("c1", {key: "value"})).toEqual(jasmine.any(State));
    expect(c.add("c2", {key: "value"})).toNotEqual(jasmine.any(SubState));
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
    s.add("child", {key: "value"});
    s.toString().should.equal(JSON.stringify({child: {key: "value"}}));
  });

  it("should root a child State when serializing", function () {
    var root = new State();
    var child = root.add("child", {key: "value"});
    child.toString().should.equal(JSON.stringify({child: {key: "value"}}));
  });
});

describe("updating", function () {
  it("should create and return a child if one does not exist", function () {
    var root = new State();
    expect(root.get("child")).toBeUndefined();
    var child = root.update("child", {key: "value"});
    child.toString().should.equal(JSON.stringify({child: {key: "value"}}));
    root.toString().should.equal(JSON.stringify({child: {key: "value"}}));
  });
  it("should overwrite updates to properties", function () {
    var root = new State();
    root.set("old", "old value");
  });
  it("should blend updates to children", function () {
  });
});
