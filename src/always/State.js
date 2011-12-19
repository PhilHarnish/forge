var events = require("events");

var State = function(data) {
  this.data = data || {};
};

State.prototype = new events.EventEmitter();

State.prototype.set = function(key, value) {
  this.data[key] = value;
  this.emit('change', key, value);
  return this.data[key];
};

State.prototype.get = function(key) {
  return this.data[key];
};

module.exports = State;
