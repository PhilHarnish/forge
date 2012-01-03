var Signal = function() {
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
  },
  signal: function() {
    var listeners = this._callback;
    if (listeners) {
      var i = 0;
      var listener = listeners[i] || listeners;
      while (listener) {
        listener.call(this, arguments);
        listener = listeners[++i];
      }
    }
  }
};

module.exports = Signal;
