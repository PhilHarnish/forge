var _ = require("../../../third_party/underscore/underscore.js")._;

var MIN = 100;
var MAX = 999;

exports.preamble = ["Finding the largest palindrome from the product of two",
  "numbers between", MIN, "and", MAX + "."];

exports.solutions = {
  brute_force: function () {
    var p = new Primes();
    var lastPrime = p.next();
    var largestFactor;
    var ceil = Math.ceil(Math.sqrt(NUM));
    do {
      lastPrime = p.next();
      if (NUM % lastPrime == 0) {
        largestFactor = lastPrime;
      }
    } while (lastPrime < ceil);
    return largestFactor;
  }
};
