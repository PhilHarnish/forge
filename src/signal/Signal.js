var Signal = function(that, fn) {
  var f = function (that, fn) {
    if (fn && typeof fn == "function") {
      return f.add(function () {
        fn.apply(that, arguments);
      });
    } else if (that && typeof that == "function") {
      return f.add(that);
    }
    return f.signal.apply(f, arguments);
  };

  for (var key in Signal.prototype) {
    f[key] = Signal.prototype[key];
  }

  arguments.length && f(that, fn);

  return f;
};

Signal.init = function(obj) {
  for (var signal in obj.signals) {
    obj[signal] = new Signal;
  }
};

Signal.prototype = {
  add: function(callback) {
    if (!this._callback) {
      this._callback = callback;
    } else if (typeof this._callback == 'function') {
      this._callback = [this._callback, callback];
    } else {
      this._callback.push(callback);
    }
    return this;
  },
  remove: function(callback) {
    var listeners = this._callback;
    if (listeners == callback) {
      delete this._callback;
    } else if (listeners && listeners.indexOf) {
      var i = listeners.indexOf(callback);
      if (i >= 0) {
        listeners.splice(i, 1);
        if (!listeners.length) {
          delete this._callback;
        } else if (listeners.length == 1) {
          this._callback = listeners[0];
        }
      }
    }
    return this;
  },
  signal: function() {
    var listeners = this._callback;
    var result;
    if (listeners) {
      var i = 0;
      var listener = listeners[i] || listeners;
      while (listener) {
        result = listener.apply(this, arguments);
        listener = listeners[++i];
      }
    }
    return result;
  }
};

module.exports = Signal;
