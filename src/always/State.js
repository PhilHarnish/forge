var events = require("events");

var State = function(path, data) {
  this._type = State;
  this._root = this; // Needed?
  this._parent = null; // Needed?
  this._path = path || "";
  this._children = {};
  this._data = {};
  this.apply(data);
};

State.prototype = new events.EventEmitter();

// TODO: Needed?
State.prototype.set = function(key, value) {
  this._data[key] = value;
  return this._data[key];
};

State.prototype.get = function(key) {
  var location = this._get(key);
  // Intentionally return undefined if path segments remain.
  return location[1].length ? undefined : location[0];
};

State.prototype._get = function (key) {
  var target = key[0] == "/" ? this._root : this;
  var path = key.split("/");
  while (path.length && target) {
    var segment = path.shift();
    if (segment) {
      if ((segment in target._children) || (segment in target._data)) {
        target = target._children[segment] || target._data[segment];
      } else {
        path.unshift(segment);
        break;
      }
    }
  }
  return [target, path];
};

// TODO: Deprecate? Private?
State.prototype.apply = function(data) {
  for (var key in data) {
    if (key in this._children) {
      this._children[key].apply(data[key]);
    } else {
      this.set(key, data[key]);
    }
  }
  return this;
};

State.prototype.group = function (key, type) {
  var child = this.add(key);
  child._type = type || child._type;
  return child;
};

// TODO: Deprecate? Private?
State.prototype.add = function(key, data) {
  var child = new this._type(this._path + "/" + key, data);
  this._children[key] = child;
  child._root = this._root;
  child._parent = this;
  return child;
};

State.prototype.post = function(path, data) {
  var location = this._get(path);
  var target = location[0];
  var incompletePath = location[1];
  // TODO: Iterate over keys in data and create recursively?
  var collectionName;
  while (incompletePath.length) {
    collectionName = incompletePath.shift();
    if (collectionName && incompletePath.length) {
      target = target.add(collectionName);
    }
  }
  // Posting to an entity, eg: /path/to/entity { ... }
  if (collectionName) {
    return target.set(collectionName, data);
  }
  // Posting to a collection, eg: /path/to/collection/ { id1: ..., id2: ... }
  for (var key in data) {
    if (key.slice(-1) == "/") {
      target.post(key, data[key]);
    } else {
      target.set(key, data[key]);
    }
  }
  return target;
};
// TODO: Deprecate.
State.prototype.update = State.prototype.post;

State.prototype._toJsonObject = function () {
  var result = {},
      key;
  for (key in this._data) {
    result[key] = this._data[key];
  }
  for (key in this._children) {
    result[key + "/"] = this._children[key]._toJsonObject();
  }
  return result;
};

State.prototype.toString = function () {
  var result = this._toJsonObject();
  // Wrap data in {"path": {"to": {"child": ...}}}, stop before root is reached.
  var path = this._path.split("/");
  while (path.length > 1) {
    var next = {};
    next[path.pop() + "/"] = result;
    result = next;
  }
  return JSON.stringify(result);
};

module.exports = State;
