var State = require("always/State.js");

var Task = function(id, data) {
  State.call(this, id, data);
  // TODO: Remove 'id'
  this.id = id.split("/").pop();
  this._data.status = this._data.status || Task.CREATED;
};

Task.CREATED = 'CREATED';
Task.PENDING = 'PENDING';
Task.COMPLETE = 'COMPLETE';
Task.TIMEOUT = 'TIMEOUT';

Task.prototype = new State();
Task.prototype.signals = {
  onComplete: true
};

Task.prototype.set = function(key, value) {
  this._data[key] = value;
  if (key == 'status' && value == Task.COMPLETE) {
    this.onComplete.signal();
  }
};

Task.prototype.isComplete = function () {
  // TODO: This is ugly.
  return this._data.status == Task.COMPLETE ||
      this._data.status == Task.TIMEOUT;
};

module.exports = Task;
