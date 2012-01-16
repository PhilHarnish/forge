var Honcho = function () {
  this._files = {};
};

var _TEST_REGEX = /Test\.js/;

Honcho.prototype = {
  addDeps: function (deps) {
    for (var file in deps) {
      this._files[file] = deps[file].concat();
    }
  },

  getFiles: function () {
    var result = [];
    for (var file in this._files) {
      result.push(file);
    }
    return result;
  },

  getTests: function () {
    var result = [];
    for (var file in this._files) {
      if (_TEST_REGEX.test(file)) {
        result.push(file);
      }
    }
    return result;
  },

  isComplete: function () {
    for (var fileIterator in this._files) {
      var deps = this._files[fileIterator];
      for (var depIndex in deps) {
        if (!(deps[depIndex] in this._files)) {
          return false;
        }
      }
    }
    return true;
  }
};

module.exports = Honcho;
