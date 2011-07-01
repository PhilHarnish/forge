var _ = require("../../../third_party/underscore/underscore.js")._;
var Primes = require("./generators.js").Primes;

exports.isPalindrome = function (n) {
  str = n.toString();
  var l = str.length ;
  var l2 = Math.ceil(l / 2);
  l--;
  for (var i = 0; i < l2; i++) {
    if (str[i] != str[l - i]) {
      return false;
    }
  }
  return true;
};

exports.factors = function (n) {
  var p = new Primes();
  var lastPrime;
  var factors = [];
  var ceil = Math.ceil(Math.sqrt(n));
  do {
    lastPrime = p.next();
    if (n % lastPrime == 0) {
      factors.push(lastPrime);
    }
  } while (lastPrime < ceil);
  return factors;
};
