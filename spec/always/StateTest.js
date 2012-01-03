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
    expect(root.get("tautology")).toBeTruthy();
    expect(root.get("contradiction")).toBeFalsy();
  });

  it("should create children with post.", function () {
    var root = new State("root");
    var child = root.post("empty/");
    expect(root.get("empty")).toEqual(child);
    child = root.post("simple/", {key: "value"});
    expect(root.get("simple").get("key")).toEqual("value");
  });

  it("should allow posting repeatedly.", function () {
    var root = new State();
    root.post("path/").post("to/", {key: "value"});
    expect(JSON.parse(root.toString())).
        toEqual({"path/": {"to/": {key: "value"}}});
  });

  it("should allow specifying type of children.", function () {
    var root = new State();
    expect(SubState).toBeDefined();
    var a = root.group("a", SubState);
    expect(a._add("a1", {key: "value"})).toEqual(jasmine.any(State));
    expect(a._add("a2", {key: "value"})).toEqual(jasmine.any(SubState));
    var b = root.group("b", State);
    expect(b._add("b1", {key: "value"})).toEqual(jasmine.any(State));
    expect(b._add("b2", {key: "value"})).toNotEqual(jasmine.any(SubState));
    var c = root.group("c");
    expect(c._add("c1", {key: "value"})).toEqual(jasmine.any(State));
    expect(c._add("c2", {key: "value"})).toNotEqual(jasmine.any(SubState));
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
    root.post("child/", {key: "value"});
    root.toString().should.equal(JSON.stringify({"child/": {key: "value"}}));
  });

  it("should root a child State when serializing", function () {
    var root = new State();
    var child = root.post("child/", {key: "value"});
    child.toString().should.equal(JSON.stringify({"child/": {key: "value"}}));
  });
});

describe("GET", function () {
  var root;
  beforeEach(function () {
    root = new State();
    root.post("path/").post("to/", {"key": "value"});
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

describe("POST", function () {
  var root;
  beforeEach(function () {
    root = new State();
    root.group("subgroup");
    root.group("substate", SubState);
  });

  it("should post multiple items to different groups at once", function () {
    var post = {
      "subgroup/": {
        "id/": { key: "value" }
      },
      "substate/": {
        "id/": { key: "value" }
      }
    };
    root.post("/", post);
    expect(JSON.parse(root.toString())).toEqual(post);
    expect(root.get("/subgroup/id")).toEqual(jasmine.any(State));
    expect(root.get("/substate/id")).toEqual(jasmine.any(SubState));
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
    var child = root.post("child/", {key: "value"});
    child.toString().should.equal(JSON.stringify({"child/": {key: "value"}}));
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
    var post = {
      "a/": {
        unique: "value",
        shared: "first"
      },
      "b/": {
        shared: "first"
      }
    };
    root.post("/", post);
    expect(JSON.parse(root.toString())).toEqual(post);
    root.post("/", {
      "a/": {
        shared: "second"
      },
      "b/": {
        unique: "value",
        shared: "second"
      }
    });
    post["a/"].shared = "second";
    post["b/"].shared = "second";
    post["b/"].unique = "value";
    expect(JSON.parse(root.toString())).toEqual(post);
  });
});

describe("Events", function () {
  var root;
  beforeEach(function () {
    root = new State();
  });

  it("should signal added states.", function () {
    expect(root.onAdded).toBeDefined();
    var results = [];
    root.onAdded.add(function (arg) {
      results.push(arg);
    });
    root.post("/", {
      "a/": {
        key: "value"
      }
    });
    expect(results.length).toEqual(1);
    expect(results[0]).toBe(root.get("a"));
    var post = {
      "b/": {
        key: "value"
      },
      "c/": {
        key: "value"
      }
    };
    root.post("/", post);
    expect(results.length).toEqual(3);
  });
});
