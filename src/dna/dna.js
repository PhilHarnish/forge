var Dna = function(seed) {
  this._value = seed || String.fromCharCode(0);
  var length = this._value.length;
  var isPow2 = length & (length + 1);
  if (length & (length + 1)) {
    throw new RangeError;
  }
};

Dna.prototype = {
  toString: function () {
    return this._value;
  },
  valueOf: function () {
    return this._value;
  }
};

module.exports = Dna;
