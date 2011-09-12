var Dna = function(seed) {
  this.value = seed || String.fromCharCode(0);
  var length = this.value.length;
  var isPow2 = length & (length + 1);
  if (length & (length + 1)) {
    throw new RangeError;
  }
};

Dna.prototype = {
  toString: function () {
    return this.value;
  },
  valueOf: function () {
    return this.value;
  }
};
