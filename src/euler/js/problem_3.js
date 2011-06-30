var _ = require("../../../third_party/underscore/underscore.js")._;

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

var Primes = function () {
  this._lastPrime = -1;
  this.next = function () {
    abort = 100;
    this._lastPrime++;
    while (abort-- && this._lastPrime >= Primes._allPrimes.length) {
      Primes._findNextPrime();
    }
    return Primes._allPrimes[this._lastPrime];
  };
};
Primes._allPrimes = [2, 3];
Primes._findNextPrime = function() {
  var candidate = _(Primes._allPrimes).last();
  var abort = 100;
  while (abort--) {
    var ceil = Math.sqrt(candidate);
    candidate += 2;
    divisible = false;
    for (var p = 0, i = 0, l = Primes._allPrimes.length;
        i < l && p < ceil;
        i++) {
      p = Primes._allPrimes[i];
      if (candidate % p == 0) {
        divisible = true;
      }
    }
    if (!divisible) {
      Primes._allPrimes.push(candidate);
      return candidate;
    }
  }
};
