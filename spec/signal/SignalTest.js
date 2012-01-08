var spec = require("../../test"),
    Signal = require("signal/Signal.js");

describe("Mixin", function () {
  it("should mixin specified signals.", function () {
    var o = {
      signals: {
        signalA: true,
        signalB: true
      }
    };
    Signal.init(o);
    expect(o.signalA.add).toBe(Signal.prototype.add);
    expect(o.signalB.add).toBe(Signal.prototype.add);
    expect(o['signalC']).toBeUndefined();
  });
});

describe("Signaling", function () {
  var s,
      callbacks,
      status;
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

describe("Shorthand", function () {
  var called,
      s,
      callback;
  beforeEach(function () {
    called = 0;
    callback = function () {
      called++;
    };
  });

  it("should take a function for pass through", function () {
    s = Signal(callback);
    s();
    expect(called).toBeTruthy();
  });

  it("should bind a function", function () {
    var o = {
      input: undefined,
      fn: function () {
        this.input = arguments;
      }
    };
    s = Signal(o, o.fn);
    s(4, 5, 6);
    expect(o.input).toEqual([4, 5, 6]);
  });

  it("should allow removal of callbacks", function () {
    s = Signal(callback);
    s.remove(callback);
    s();
    expect(called).toBeFalsy();
  });

  it("should function chain", function () {
    s = Signal();
    s(callback)(callback);
    s();
    expect(called).toBe(2);
  });

  describe("events", function () {
    var onEvent;
    beforeEach(function () {
      onEvent = Signal();
    });

    it("should add multiple callbacks after construction", function () {
      onEvent(callback);
      onEvent();
      expect(called).toBeTruthy();
      expect(called).toBe(1);
      onEvent(callback);
      onEvent();
      expect(called).toBe(3);
    });
  });
});

describe("Composing", function () {
  var sequence,
      callbacks,
      s;
  var callback = function (name) {
    if (!callbacks[name]) {
      callbacks[name] = function (input) {
        var args = JSON.stringify(Array.prototype.slice.call(arguments, 0));
        sequence.push(name + "(" + args.slice(1, -1) + ")");
        return name + input;
      };
    }
    return callbacks[name];
  };

  beforeEach(function () {
    sequence = [];
    callbacks = {};
    s = Signal();
  });

  it("should call sequences in order", function () {
    s(callback("A"))(callback("B"))(callback("C"));
    s();
    expect(sequence).toEqual(["A()", "B()", "C()"]);
  });

  it("should call nested callbacks outside -> in", function () {
    s(Signal(callback("A"))
        (callback("A1"))(callback("A2"))
    );
    s(callback("B"));
    s();
    expect(sequence).toEqual(["A()", "A1()", "A2()", "B()"]);
  });

  describe("return values", function () {
    it ("should return simple values", function () {
      s(callback("A"));
      expect(s(1)).toEqual("A1");
    });

    it("should return the last value", function () {
      s(callback("A"))(callback("B"));
      expect(s(1)).toEqual("B1");
      expect(sequence).toEqual(["A(1)", "B(1)"]);
    });
  });
});
