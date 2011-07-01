var _ = require("../../../third_party/underscore/underscore.js")._;

var MAX = 20;

exports.preamble = ["Smallest number evenly divisible by numbers between 1 and",
  MAX];

exports.solutions = {
  brute_force: function () {
    var candidate = MAX * 2;
    while (candidate) {
      var i;
      for (i = 1; i <= MAX && candidate % i == 0; i++) {
      }
      if (i > MAX) {
        return candidate;
      } else {
        candidate += 2;
      }
    }
    return 404;
  }
};
