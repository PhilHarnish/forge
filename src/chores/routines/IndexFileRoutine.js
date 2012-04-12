var Chore = require("chores/Chore.js"),
    Routine = require("chores/Routine.js");

var IndexFileRoutine = function () {
  Routine.apply(this);
};

IndexFileRoutine.prototype = new Routine();

IndexFileRoutine.prototype.cost = function (chore) {
  return 1; // ms
};


exports.module = IndexFileRoutine;

