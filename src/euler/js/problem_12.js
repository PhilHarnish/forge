var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;
var divisors = require("./util.js").divisors;

var DIVISORS = 500;

exports.preamble = ["Finding the first triangle number to have over", DIVISORS,
  "divisors."];

exports.solutions = {
  brute_force: function () {
    var accumulator = 1;
    var counter = 2;
    var numDivisors = 0;
    while (numDivisors < DIVISORS) {
      accumulator += counter;
      counter++;
      var ceil = accumulator / 2;
      numDivisors = divisors(accumulator).length;
    }
    return accumulator;
  }
};
