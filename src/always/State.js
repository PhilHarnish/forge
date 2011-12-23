var events = require("events");

var State = function(path, data) {
  this._type = State;
  this._path = path || "";
  this._children = {};
  this._data = {};
  this.apply(data);
};

State.prototype = new events.EventEmitter();

State.prototype.set = function(key, value) {
  this._data[key] = value;
  return this._data[key];
};

State.prototype.get = function(key) {
  return this._children[key] || this._data[key];
};

State.prototype.apply = function(data) {
  for (var key in data) {
    if (key in this._children) {
      this._children[key].apply(data[key]);
    } else {
      this.set(key, data[key]);
    }
  }
};

State.prototype.group = function (key, type) {
  var child = this.add(key);
  child._type = type || child._type;
  return child;
};

State.prototype.add = function(key, data) {
  this._children[key] = new this._type(this._path + "/" + key, data);
  return this._children[key];
};

State.prototype.update = function(key, data) {
  // TODO: Update existing children!
  return this._children[key] || this.add(key, data);
};

State.prototype._toJsonObject = function () {
  var result = {},
      key;
  for (key in this._data) {
    result[key] = this._data[key];
  }
  for (key in this._children) {
    result[key] = this._children[key]._toJsonObject();
  }
  return result;
};

State.prototype.toString = function () {
  var result = this._toJsonObject();
  // Wrap data in {"path": {"to": {"child": ...}}}, stop before root is reached.
  var path = this._path.split("/");
  while (path.length > 1) {
    var next = {};
    next[path.pop()] = result;
    result = next;
  }
  return JSON.stringify(result);
};

module.exports = State;
