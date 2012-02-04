var spec = require("../../test"),
    Hyve = require("hyve/Hyve.js");

var hyve, c;
var setup = function () {
  hyve = new Hyve();
};
var sample = {key: "value"};

xdescribe("Paths", function () {
  beforeEach(setup);

  it("should be rooted", function () {
    expect(hyve.dirName).toBe("");
  });
});

xdescribe("Signaling", function () {
  beforeEach(setup);

  var signalData;
  var onSignal = function (data) {
    signalData = data;
  };

  it("should support synchronous gets", function () {
    var result = hyve.post("", sample);
    hyve.get(result.dirName, onSignal);
    expect(signalData).toEqual(sample);
  });

  it("should support asynchronous gets", function () {
    hyve.get(Signal.hash(sample), onSignal);
    var result = hyve.post("", sample);
    expect(signalData).toEqual(sample);
  });

  it("should signal listeners when data is appended", function () {
    var c = hyve.post("collection", {});
    c.post("update", sample);
    expect(signalData).toEqual(sample);
  });
});
