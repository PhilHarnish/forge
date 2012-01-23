var uuid = require("node-uuid/uuid.js"),
    Signal = require("signal/Signal.js");

var Resource = function (id, fileName, contents, type) {
  this.id = id;
  this.fileName = fileName;
  this.contents = contents;
  this.type = type;
  this.onReferencesAdded = new Signal();
  this.references = {};
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
  }
};

module.exports = Resource;
