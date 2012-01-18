var Honcho = function () {
  this._source = {};
};

var _TEST_REGEX = /Test\.js/;

Honcho.prototype = {
  addDeps: function (deps) {
    for (var file in deps) {
      this._source[file] = {
        deps: deps[file].concat()
      };
    }
  },

  getFiles: function () {
    var result = [];
    for (var file in this._source) {
      result.push(file);
    }
    return result;
  },

  getTests: function () {
    var result = [];
    for (var file in this._source) {
      if (_TEST_REGEX.test(file)) {
        result.push(file);
      }
    }
    return result;
  },

  isComplete: function () {
    for (var fileIterator in this._source) {
      var deps = this._source[fileIterator];
      for (var depIndex in deps.deps) {
        if (!(deps.deps[depIndex] in this._source)) {
          return false;
        }
      }
    }
    return true;
  }
};

module.exports = Honcho;
