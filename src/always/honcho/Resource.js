var crypto = require('crypto'),

    uuid = require("node-uuid/uuid.js"),

    Signal = require("signal/Signal.js");

var Resource = function (id, fileName, contents, type) {
  this.id = id;
  this.fileName = fileName;
  this.contents = contents;
  this.digest = null;
  this.type = type;
  this.onReferencesAdded = new Signal();
  this.onContentsChanged = new Signal();
  this.onStatsChanged = new Signal();
  this.references = {};
  this.deps = [];
  // TODO: This is lame. Need some way of tracking async changes.
  this.writeLock = false;
};

Resource.fromFileName = function (fileName) {
  var id = uuid();
  var resource = new Resource(id, fileName, null, null);
  var references = {};
  references[id] = 1;
  resource.rename(fileName);
  resource.addReferences(references);
  return resource;
};

Resource.prototype = {
  addReferences: function (references) {
    for (var key in references) {
      this.references[key] = references[key];
    }
    this.onReferencesAdded(references);
  },

  setContents: function (contents) {
    this.contents = contents;
    var shaHash = crypto.createHash("sha1");
    shaHash.update(contents);
    this.digest = shaHash.digest("hex");
    var references = {};
    references[this.digest] = 1;
    this.addReferences(references);
    this.onContentsChanged(this, contents);
  },

  rename: function (fileName) {
    var inputIsAbsolute = fileName[0] == "/";
    // Never rename if it would make resource path less absolute.
    // TODO: Tests. Does this even happen?
    if (this.fileName[0] != "/" || inputIsAbsolute) {
      this.fileName = fileName;
    }
    // Always add aliases.
    var references = {};
    references[fileName] = inputIsAbsolute ? 1 : .8;
    var parts = fileName.split("/");
    var segments = parts.length;
    while (parts.length) {
      if (parts[0]) {
        // (n / t) for n out of t remaining parts, halved.
        references[parts.join("/")] = (parts.length / segments) / 2;
      }
      parts.shift();
    }
    this.addReferences(references);
  }
};

module.exports = Resource;
