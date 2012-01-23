var fs = require("fs"),

    Index = require("always/honcho/Index.js"),
    Resource = require("always/honcho/Resource.js"),
    Signal = require("signal/Signal.js");

var Honcho = function () {
  this._index = new Index();
};

Honcho.prototype = {
  addFileName: function (fileName) {
    if (!this._index.find(fileName)) {
      var resource = Resource.fromFileName(fileName);
      this._getFileContents(resource);
      this._index.add(resource);
    }
  },

  _getFileContents: function (resource) {
    fs.readFile(resource.fileName, function (err, data) {
      resource.setContents(data);
    });
  },

  find: function (reference) {
    return this._index.find(reference);
  }
};

module.exports = Honcho;
