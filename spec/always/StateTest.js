var spec = require("../../test"),
    State = require("always/State.js");

var SubState = function (path, data) {
  State.call(this, path, data);
};
SubState.prototype = new State();

describe("Construction", function () {
  it("should accept constructor arguments.", function () {
    var root = new State("test", {tautology: true,
        contradiction: false});
    root.get("tautology").should.equal(true);
    root.get("contradiction").should.equal(false);
  });

  it("should create children with post.", function () {
    var root = new State();
    var child = root.post("empty");
    root.get("empty").should.equal(child);
    child = root.post("simple", {key: "value"});
    root.get("simple").get("key").should.equal("value");
  });

  it("should allow posting repeatedly.", function () {
    var root = new State();
    root.post("path").post("to", {key: "value"});
    expect(JSON.parse(root.toString())).toEqual({path: {to: {key: "value"}}});
  });

  it("should allow specifying type of children.", function () {
    var root = new State();
    expect(SubState).toBeDefined();
    var a = root.group("a", SubState);
    expect(a.add("a1", {key: "value"})).toEqual(jasmine.any(State));
    expect(a.add("a2", {key: "value"})).toEqual(jasmine.any(SubState));
    var b = root.group("b", State);
    expect(b.add("b1", {key: "value"})).toEqual(jasmine.any(State));
    expect(b.add("b2", {key: "value"})).toNotEqual(jasmine.any(SubState));
    var c = root.group("c");
    expect(c.add("c1", {key: "value"})).toEqual(jasmine.any(State));
    expect(c.add("c2", {key: "value"})).toNotEqual(jasmine.any(SubState));
  });
});

describe("toString()", function () {
  it("should serialize an empty State.", function () {
    var root = new State();
    root.toString().should.equal("{}");
  });

  it("should serialize a simple root State.", function () {
    var root = new State();
    root.set("key", "value");
    root.toString().should.equal(JSON.stringify({key: "value"}));
  });


  it("should serialize a root State with children.", function () {
    var root = new State();
    root.add("child", {key: "value"});
    root.toString().should.equal(JSON.stringify({child: {key: "value"}}));
  });

  it("should root a child State when serializing", function () {
    var root = new State();
    var child = root.add("child", {key: "value"});
    child.toString().should.equal(JSON.stringify({child: {key: "value"}}));
  });
});

describe("GET", function () {
  var root;
  beforeEach(function () {
    root = new State();
    root.post("path").post("to", {"key": "value"});
  });

  it("should traverse absolute paths", function () {
    root.get("/").should.equal(root);
    root.get("/path/to/key").should.equal("value");
    root.get("/path/to").get("/path/to/key").should.equal("value");
    expect(root.get("/path/to").get("/key")).toBeUndefined();
  });

  it("should traverse relative paths", function () {
    expect(root.get("path")).toBeDefined();
    root.get("path/to/key").should.equal("value");
    root.get("path/to").get("key").should.equal("value");
  });
});

describe("Updating", function () {
  var root;
  beforeEach(function () {
    root = new State();
  });

  it("should set and get.", function () {
    expect(root.get("lost")).toBeUndefined();
    root.set("found", "value").should.equal("value");
  });

  it("should create and return a child if one does not exist", function () {
    expect(root.get("child")).toBeUndefined();
    var child = root.post("child", {key: "value"});
    child.toString().should.equal(JSON.stringify({child: {key: "value"}}));
  });

  it("should overwrite updates to properties", function () {
    root.set("old", "old value");
    root.apply({
        "old": "updated value",
        "new": "new value"
      });
    root.get("old").should.equal("updated value");
    root.get("new").should.equal("new value");
  });

  it("should blend updates to children", function () {
    var a = root.group("a");
    var expected = {
      a: {
        unique: "value",
        shared: "first"
      },
      b: {
        shared: "first"
      }
    };
    root.post("/", expected);
    expect(JSON.parse(root.toString())).toEqual(expected);
    root.post("/", {
      a: {
        shared: "second"
      },
      b: {
        unique: "value",
        shared: "second"
      }
    });
    expected.a.shared = "second";
    expected.b.shared = "second";
    expected.b.unique = "value";
    expect(JSON.parse(root.toString())).toEqual(expected);
  });
});
