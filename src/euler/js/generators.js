var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;

var Primes = function () {
  var lastPrime = -1;
  this.next = function () {
    abort = 100;
    lastPrime++;
    while (abort-- && lastPrime >= Primes._allPrimes.length) {
      Primes._findNextPrime();
    }
    return Primes._allPrimes[lastPrime];
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

exports.Primes = Primes;

var Fibonacci = function () {
  var last = bc(1);
  var penultimate = bc(1);
  this.next = function () {
    var farthest = penultimate;
    var next = bc.sum(last, penultimate);
    penultimate = last;
    last = next;
    return farthest;
  };
};

exports.Fibonacci = Fibonacci;
