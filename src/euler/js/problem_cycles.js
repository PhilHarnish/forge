var _ = require("../../../third_party/underscore/underscore.js")._;

var LENGTH = 9;
var BASE = 2;

/*
A000031 = function (n) {
  var d, s;
  if n == 0 {
    return 1;
  } else {
    s = 0;
    for d in divisors(n) {
      s += phi(d) * (2^(n/d));
    }
  }
  return s / n;
}
 */


exports.preamble = ["Finding the number of cycles of length", LENGTH,
  "in an alphabet of length", BASE];

exports.solutions = {
  brute_force: function () {
    var max = Math.pow(BASE, LENGTH);
    var count = 0;
    var known = {};
    for (var i = 0; i < max; i++) {
      var digits = pad(i.toString(BASE), LENGTH);
      var min = digits;
      for (var j = 0; j < LENGTH; j++) {
        var next = digits.slice(1) + digits[0];
        if (min > next) {
          min = next;
        }
        digits = next;
      }
      if (!known[min]) {
        known[min] = true;
        console.log(min);
        count++;
      }
    }
    return count;
  }
};

function pad(str, length) {
  while (str.length < length) {
    str = "0" + str;
  }
  return str;
}
