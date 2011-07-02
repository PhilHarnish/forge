var fs = require("fs");
var path = require("path");
var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;
var divisors = require("./util.js").divisors;
var Fibonacci = require("./generators.js").Fibonacci;

var TERM = 1000000;
var DIGITS = "0123456789".split("");

exports.preamble = ["Finding the", TERM + "th term in lexicographic",
  "permutations of", DIGITS.join(", ") + "."];

exports.solutions = {
  brute_force: function () {
    var result = "";
    var counter = 0;
    var permute = function(digits, term) {
      var digit = false;
      for (var i = 0; i < digits.length; i++) {
        if (digits[i]) {
          digit = digits[i];
          digits[i] = false;
          permute(digits, term + digit);
          digits[i] = digit;
        }
      }
      if (!digit) {
        counter++;
        if (counter == TERM) {
          result = term;
        }
      }
    };
    permute(_(DIGITS).clone(), "");
    return result;
  }
};
