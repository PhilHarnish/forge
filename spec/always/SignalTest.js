var spec = require("../../test"),
    Signal = require("always/Signal.js");

describe("Mixin", function () {
  it("should mixin specified signals.", function () {
    var o = {
      signals: {
        signalA: true,
        signalB: true
      }
    };
    Signal.init(o);
    expect(o.signalA).toEqual(jasmine.any(Signal));
    expect(o.signalB).toEqual(jasmine.any(Signal));
    expect(o['signalC']).toBeUndefined();
  });
});

describe("Signaling", function () {
  var s,
      callbacks = [],
      status = [];
  var getCallback = function (i) {
    if (!callbacks[i]) {
      callbacks[i] = function (arg) {
        var increment = arg || 1;
        status[i] = (status[i] || 0) + increment;
      };
    }
    return callbacks[i];
  };
  beforeEach(function () {
    s = new Signal;
    callbacks = [];
    status = [];
  });

  it("should ignore signal with no listeners.", function () {
    s.signal();
    expect(status[0]).toBeFalsy();
  });

  it("should remove added functions.", function () {
    s.add(getCallback(0));
    s.remove(getCallback(0));
    s.signal();
    expect(status[0]).toBeFalsy();
  });

  it("should signal added functions.", function () {
    s.add(getCallback(0));
    s.signal();
    expect(status[0]).toEqual(1);
  });

  it("should preserve unrelated functions.", function () {
    s.add(getCallback(0));
    s.remove(getCallback(1));
    s.signal();
    expect(status[0]).toEqual(1);
  });

  it("signal should pass along args", function () {
    s.add(getCallback(0));
    s.signal(5);
    expect(status[0]).toEqual(5);
    s.signal(2);
    expect(status[0]).toEqual(7);
  });

  it("should handle complex sequences of add/remove/signal", function () {
    var testCases = [
        0, [], // No-op.
        1, [1], // Add 1 callback.
        2, [2, 1, 1], // Add 2 more callbacks.
        1, [3, 2, 2, 1], // Add one last callback.
        -2, [4, 3, 2, 1], // Remove two, call first two.
        0, [5, 4, 2, 1], // Call first two again.
        -1, [6, 4, 2, 1], // Remove 2nd, call first.
        -1, [6, 4, 2, 1], // Remove last one.
        0, [6, 4, 2, 1] // Verify none called.
    ];
    var index = 0;
    for (var i = 0; i < testCases.length / 2; i += 2) {
      var delta = testCases[i];
      var expected = testCases[i + 1];
      while (delta > 0) {
        // Add callbacks specified by delta, increment index afterwards.
        s.add(getCallback(index++));
        delta--;
      }
      while (delta < 0) {
        // Decrement index and remove matching callback.
        s.remove(getCallback(--index));
        delta++;
      }
      s.signal();
      expect(status).toEqual(expected);
    }
  });
});
