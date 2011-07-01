var _ = require("../../../third_party/underscore/underscore.js")._;
var Primes = require("./generators.js").Primes;

var TARGET = 1000;

exports.preamble = ["Finding the product of a Pythagorean triplet whose sum is",
    TARGET + "."];

exports.solutions = {
  brute_force: function () {
    var a = 0;
    while (a < TARGET) {
      a++;
      var b = a + 1;
      var c = TARGET - a - b;
      while (b < c) {
        if (a * a + b * b == c * c) {
          console.log(a, b, c);
          if (a + b + c == TARGET) {
            return a * b * c;
          }
        }
        b++;
        c = TARGET - (a + b);
      }
    }
    return 404;
  }
};
