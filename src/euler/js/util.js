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
  var ceil = Math.ceil(n / 2);
  do {
    lastPrime = p.next();
    if (n % lastPrime == 0) {
      factors.push(lastPrime);
    }
  } while (lastPrime < ceil);
  return factors;
};

exports.inOrderMerge = function(a, b) {
  var result = [];
  var al = a.length;
  var bl = b.length;
  var ai = 0;
  var bi = 0;
  while (ai < al && bi < bl) {
    var d = a[ai] - b[bi];
    if (d < 0) {
      result.push(a[ai]);
      ai++;
    } else if (d == 0) {
      result.push(a[ai]);
      ai++;
      bi++;
    } else {
      result.push(b[bi]);
      bi++;
    }
  }
  while (ai < al) {
    result.push(a[ai]);
    ai++;
  }
  while (bi < bl) {
    result.push(b[bi]);
    bi++;
  }
  return result;
};

var _divisorCache = [[], [1]];
exports.divisors = function (n) {
  if (_divisorCache[n]) {
    return _divisorCache[n];
  }
  var factors = exports.factors(n);
  //console.log('factors', n, factors);
  var divisors = [1];
  _(factors).each(function (i) {
    //console.log('looking up', n / i);
    var temp = exports.divisors(n / i);
    //console.log('found', temp);
    divisors = exports.inOrderMerge(divisors, temp);
  });
  divisors.push(n);
  _divisorCache[n] = divisors;
  return divisors;
};

/*
console.log(exports.inOrderMerge([1,5,10], [1,2,3,4,5,6,7,20]));

for (var i = 2; i <= 25; i++) {
  console.log(i, exports.divisors(i));
}

_(_divisorCache).each(function (v, k) {
  console.log(k, v);
});
*/
