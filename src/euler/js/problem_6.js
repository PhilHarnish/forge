var _ = require("../../../third_party/underscore/underscore.js")._;

var MAX = 100;

exports.preamble = ["Difference between the square of the sum and the sum of",
  "squares for 1 to", MAX];

exports.solutions = {
  brute_force: function () {
    innerSum = 0;
    squareSum = 0;
    for (var i = 1; i <= MAX; i++) {
      innerSum += i;
      squareSum += i * i;
    }
    return innerSum * innerSum - squareSum;
  }
};
