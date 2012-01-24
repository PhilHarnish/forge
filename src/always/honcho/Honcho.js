var fs = require("fs"),

    Index = require("always/honcho/Index.js"),
    interpret = require("always/honcho/interpret.js"),
    Resource = require("always/honcho/Resource.js"),
    Signal = require("signal/Signal.js");

var Honcho = function () {
  this._index = new Index();
};

Honcho.prototype = {
  addFileName: function (fileName) {
    var resource = this.resolve(fileName);
    if (!resource.contents && !resource.writeLock) {
      resource.writeLock = true;
      this._getFileContents(resource.fileName, function (err, data) {
        resource.writeLock = false;
        resource.setContents(data);
      });
    }
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

  _getFileContents: fs.readFile,

  _onContentsChanged: function (resource, contents) {
    resource.type = interpret.identify(resource);
    var interpretation = interpret.interpret(resource);
    resource.deps = interpretation.deps;
    for (var i = 0; i < resource.deps.length; i++) {
      this.resolve(resource.deps[i]);
    }
  }
};

module.exports = Honcho;
