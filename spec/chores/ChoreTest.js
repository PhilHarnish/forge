var Chore = require("chores/Chore.js");

describe("Chore", function () {
  var chore,
      work = jasmine.createSpy("work");
  beforeEach(function () {
    work.reset();
    chore = new Chore(work);
  });

  describe("value", function () {
    it("should initially be undefined", function () {
      expect(chore.value()).toBeUndefined();
    });

    it("should return value on set", function () {
      expect(chore.value("set value")).toEqual("set value");
    });
  });

  describe("completion", function () {
    it("should be 100% complete on assignment, by default", function () {
      chore.value(true);
      expect(chore.completion()).toEqual(1);
    });
  });

  it("should bind 'callback'", function () {
    chore = new Chore(work);
    var fn = chore.callback;
    fn();
    expect(work).toHaveBeenCalled();
  });

  it("should bind 'invalidate'", function () {
    chore.value(true);
    var fn = chore.invalidate;
    fn();
    expect(chore.completion()).toEqual(0);
  });

  describe("value monitoring", function () {
    it("should call onProgress for updates", function () {
      var spy = jasmine.createSpy("onProgress");
      chore.onProgress(spy);
      chore.value(true);
      expect(spy).toHaveBeenCalled();
    });
    
    it("should call onRegress for invalidation", function () {
      var spy = jasmine.createSpy("onRegress");
      chore.onRegress(spy);
      chore.invalidate();
      expect(spy).toHaveBeenCalled();
    });

    it("should support incremental updates", function () {
      var values = [.1, .5, .75, 1];
      var spy = jasmine.createSpy("onProgress");
      chore.onProgress(spy);
      for (var i = 0; i < values.length; i++) {
        chore.value(values[i], values[i]);
        expect(spy).toHaveBeenCalled();
        spy.reset();
      }
    });

    it("should support decremental updates", function () {
      var values = [.1, .5, .75, 1].reverse();
      var spy = jasmine.createSpy("onRegress");
      chore.onRegress(spy);
      chore.value(true);
      for (var i = 0; i < values.length; i++) {
        chore.value(values[i], values[i]);
        expect(spy).toHaveBeenCalled();
        spy.reset();
      }
    });

    it("should call both onRegress then onProgress for refresh", function () {
      var onRegress = jasmine.createSpy("onRegress");
      var onProgress = jasmine.createSpy("onProgress");
      chore.value(1);
      chore.onRegress(onRegress);
      chore.onProgress(onProgress);
      chore.value(2);
      expect(onRegress).toHaveBeenCalled();
      expect(onProgress).toHaveBeenCalled();
    });
  });

  describe("profiling", function () {
    var profiler;
    beforeEach(function () {
      profiler = {
        start: function () {},
        end: function () {}
      };
      spyOn(profiler, "start", true);
      spyOn(profiler, "end", true);
      chore = new Chore(work, profiler);
    });

    it("should be disabled initially", function () {
      expect(profiler.start).not.toHaveBeenCalled();
      expect(profiler.end).not.toHaveBeenCalled();
      chore.work();
      expect(profiler.start).not.toHaveBeenCalled();
      expect(profiler.end).not.toHaveBeenCalled();
    });

    it("should enable with call to profile()", function () {
      chore.profile();
      chore.work();
      expect(profiler.start).toHaveBeenCalledWith(chore);
      expect(profiler.end).toHaveBeenCalledWith(chore);
    });

    it("should disable with call to profile(false)", function () {
      chore.profile();
      chore.work();
      expect(profiler.start).toHaveBeenCalled();
      expect(profiler.end).toHaveBeenCalled();
      profiler.start.reset();
      profiler.end.reset();
      chore.profile(false);
      expect(profiler.start).not.toHaveBeenCalled();
      expect(profiler.end).not.toHaveBeenCalled();
    });
  });
});
