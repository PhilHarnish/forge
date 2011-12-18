var events = require("events");

var Task = function(id, data) {
  this.id = id;
  this.data = data;
  this.state = {
    task: {}
  };
  this.state.task[id] = data;
};

Task.CREATED = 'CREATED';
Task.PENDING = 'PENDING';
Task.COMPLETE = 'COMPLETE';
Task.TIMEOUT = 'TIMEOUT';

Task.prototype = new events.EventEmitter();

Task.prototype.set = function(key, value) {
  this.data[key] = value;
  this.emit('change', key, value);
  if (key == 'status') {
    // Emit 'created', 'pending', 'complete', 'timeout', etc.
    this.emit(value);
  }
};

Task.prototype.isComplete = function () {
  return this.data.status == Task.COMPLETE ||
      this.data.status == Task.TIMEOUT;
};

Task.prototype.toState = function () {
  return this.state;
};

module.exports = Task;
