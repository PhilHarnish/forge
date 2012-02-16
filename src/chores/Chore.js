var Signal = require("signal/Signal.js");

/**
 * A chore represents the stateful execution of a Routine.
 *
 * Because a chore can be symlinked to another identical chore,
 * indirection must be used for most getters.
 */

var Chore = function (work, profiler, input) {
  this._work = work;
  this._profiler = profiler;
  this._input = input;
  // By default, "work()" calls _work directly.
  this.work = work;
  this._value = undefined;
  this._completion = 0;
  this.onProgress = new Signal(this, this._onProgress);
  this.onRegress = new Signal(this, this._onRegress);
  var that = this;
  this.invalidate = function () {
    that._invalidate();
  };
  this.callback = function () {
    that.work.apply(that, arguments);
  };
};

Chore.prototype = {
  value: function (value, completion) {
    if (arguments.length) {
      this._value = value;
      this.completion(completion === undefined ? 1 : completion);
    }
    return this._value;
  },

  completion: function (completion) {
    if (arguments.length) {
      var old = this._completion;
      this._completion = completion;
      if (completion <= old) {
        this.onRegress(this);
      }
      if (completion >= old) {
        this.onProgress(this);
      }
    }
    return this._completion;
  },

  /**
   * Perform profiling.
   * @param profile optional; default true.
   */
  profile: function (profile) {
    this.work = profile === false ? this._work : this._profileWork;
  },

  _profileWork: function () {
    this._profiler.start(this);
    this._work.apply(null, arguments);
    this._profiler.end(this);
  },

  _onRegress: function () {
  },

  _onProgress: function () {
  },

  _invalidate: function () {
    this.completion(0);
  }
};

module.exports = Chore;
