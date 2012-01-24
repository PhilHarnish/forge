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
  references[fileName] = .8;
  references[fileName.split("/").pop()] = .25;
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
  }
};

module.exports = Resource;
