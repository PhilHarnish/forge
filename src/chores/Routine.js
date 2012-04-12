/**
 * A routine is a heirarchical task network.
 *
 * The network takes the form of a directed asyclic graph with a goal at
 * the root and subroutines as children.
 */

var Routine = function () {
  this._activeChores = {};
};

Routine.prototype = {
  foo: function () {
    //return 1;
  },
  chore: function () {
    return new Chore(this, Array.prototype.slice.call(arguments));
  },
  cost: function () {
    throw new Error("Not implemented.");
  }
};

module.exports = Routine;
