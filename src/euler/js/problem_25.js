var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;
var divisors = require("./util.js").divisors;
var Fibonacci = require("./generators.js").Fibonacci;

var DIGITS = 1000;

exports.preamble = ["Finding the first Fibonacci number with", DIGITS,
  "digits."];

exports.solutions = {
  brute_force: function () {
    var f = new Fibonacci();
    var n;
    var term = 0;
    do {
      term++;
      n = f.next();
    } while (!n[DIGITS - 1]);
    return term;
  }
};
