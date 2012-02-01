var fs = require("fs"),

    Index = require("always/honcho/Index.js"),
    interpret = require("always/honcho/interpret.js"),
    Resource = require("always/honcho/Resource.js"),
    Signal = require("signal/Signal.js");

var Honcho = function () {
  this._index = new Index();
};

Honcho.prototype = {
  load: function (fileName) {
    var resource = this.resolve(fileName);
    if (!resource.contents && !resource.writeLock) {
      resource.writeLock = true;
      this._getFileContents(resource.fileName, function (err, data) {
        resource.writeLock = false;
        resource.setContents(data.toString());
      });
    }
  },

  loadDir: function (dirName) {
    var that = this;
    fs.readdir(dirName, function (err, files) {
      for (var i = 0; i < files.length; i++) {
        var file = files[i];
        if (file != "third_party" && file[0] != ".") {
          that._loadRecursiveStat(dirName + "/" + file);
        }
      }
    });
  },

  _loadRecursiveStat: function (path) {
    var that = this;
    fs.stat(path, function (err, stats) {
      if (stats.isDirectory()) {
        that.loadDir(path);
      } else {
        that.load(path);
      }
    });
  },

  find: function (reference) {
    return this._index.find(reference);
  },

  resolve: function (fileName) {
    var result = this.find(fileName);
    if (!result) {
      result = Resource.fromFileName(fileName);
      result.onContentsChanged(this, this._onContentsChanged);
      this._index.add(result);
    }
    return result;
  },

  test: function (path) {
    var tests = {};
    // Hacky! Find a better way to get all tests.
    for (var key in this._index._index) {
      var resource = this._index._index[key];
      if (!(resource.id in tests) && resource.type && resource.type.test) {
        if (resource.fileName.indexOf("SignalTest") >= 0) {
          console.log("Is test:", resource.fileName);
          tests[resource.id] = resource;
          require(resource.fileName);
          return;
        }
      }
    }
  },

  _getFileContents: fs.readFile,

  _onContentsChanged: function (resource, contents) {
    resource.type = interpret.identify(resource);
    var interpretation = interpret.interpret(resource);
    resource.deps = interpretation.deps;
    if (resource.deps) {
      for (var i = 0; i < resource.deps.length; i++) {
        this.resolve(resource.deps[i]);
      }
    }
  }
};

module.exports = Honcho;
