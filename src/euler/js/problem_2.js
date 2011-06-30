var _ = require("../../../third_party/underscore/underscore.js")._;

var CEIL = 4000000;

exports.preamble = ["Finding the sum of all the even Fibonacci below",
  CEIL + "."];

exports.solutions = {
  brute_force: function () {
    var fLast = 1;
    var fTotal = 2;
    var sum = 0;
    while (fTotal < CEIL) {
      if (fTotal % 2 == 0) {
        sum += fTotal;
      }
      var next = fTotal;
      fTotal = fLast + fTotal;
      fLast = next;
    }
    return sum;
  }
};
