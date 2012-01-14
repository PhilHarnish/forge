var Signal = require("signal/Signal.js");

var _hashId = 0;

var Hyve = function (dirName, resource) {
  this.dirName = dirName;
  this.resource = resource;
  this._journal = [];

  this.onAdded = Signal();
};

Hyve._objectCache = {};

Hyve.prototype.post = function (collection, resource) {
  var baseName = this.hash(resource);
  var path = this.dirName + "/" + baseName;
  var child = new Hyve(path, resource);
  Hyve._objectCache[baseName] = child;
  // Store baseNames? Children? Make it easier to convert one to the other?
  this._journal.push(baseName);
  this.onAdded(child);
  return child;
};

Hyve.prototype.get = function (key, onData) {
  return this;
};

Hyve.prototype.hash = function (value) {
  // TODO: SHA1 hashing for value.
  if (!value.__id__) {
    value.__id__ = _hashId++;
  }
  return value.__id__;
};

module.exports = Hyve;
