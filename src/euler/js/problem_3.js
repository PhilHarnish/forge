var _ = require("../../../third_party/underscore/underscore.js")._;
var Primes = require("./generators.js").Primes;

var NUM = 600851475143;
//var NUM = 13195;
//var NUM = 15;

exports.preamble = ["Finding the largest prime factor in", NUM + "."];

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
