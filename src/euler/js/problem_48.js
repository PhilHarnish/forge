var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;
var divisors = require("./util.js").divisors;
var Fibonacci = require("./generators.js").Fibonacci;

var CEIL = 1000;

exports.preamble = ["Find the last 10 digits of the sum n^n for n 1.." + CEIL +
  "."];

exports.solutions = {
  brute_force: function () {
    bc.TRUNCATE = 10;
    var i = 0;
    var n = bc(0);
    while (i++ < CEIL) {
      n = bc.sum(n, bc.pow(bc(i), i));
    }
    bc.TRUNCATE = Infinity;
    return bc.valueOf(n).substr(-10);
  }
};
