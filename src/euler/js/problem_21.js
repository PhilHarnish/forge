var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;
var divisors = require("./util.js").divisors;
var Fibonacci = require("./generators.js").Fibonacci;

var CEIL = 10000;

exports.preamble = ["Finding the sum of all the amicable numbers under", CEIL +
  "."];

exports.solutions = {
  brute_force: function () {
    var cache = [0];
    var total = 0;
    for (var i = 1; i < CEIL; i++) {
      var d = divisors(i);
      var sum = 0;
      var l = d.length - 1; // Skip last divisor
      while (l--) {
        sum += d[l];
      }
      cache[i] = sum;
      if (sum < i && cache[sum] == i) {
        total += i + sum;
      }
    }
    return total;
  }
};
