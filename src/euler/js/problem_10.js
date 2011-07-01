var _ = require("../../../third_party/underscore/underscore.js")._;
var Primes = require("./generators.js").Primes;

var CEIL = 2000000;

exports.preamble = ["Finding the sum of all primes below", CEIL + "."];

exports.solutions = {
  brute_force: function () {
    var p = new Primes();
    var prime = 0;
    var sum = 0;
    while (prime < CEIL) {
      sum += prime;
      prime = p.next();
    }
    return sum;
  }
};
