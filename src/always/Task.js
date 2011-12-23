var events = require("events"),

    State = require("always/State.js");

var Task = function(id, data) {
  State.call(this, id, data);
  this._type = Task;
  // TODO: Remove 'id'
  this.id = id.split("/").pop();
  this._data.status = this._data.status || Task.CREATED;
};

Task.CREATED = 'CREATED';
Task.PENDING = 'PENDING';
Task.COMPLETE = 'COMPLETE';
Task.TIMEOUT = 'TIMEOUT';

Task.prototype = new State();

Task.prototype.set = function(key, value) {
  this._data[key] = value;
  this.emit('change', key, value);
  if (key == 'status') {
    // Emit 'created', 'pending', 'complete', 'timeout', etc.
    this.emit(value);
  }
};

Task.prototype.isComplete = function () {
  return this._data.status == Task.COMPLETE ||
      this._data.status == Task.TIMEOUT;
};

module.exports = Task;
