var fs = require("fs");
var path = require("path");
var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;
var divisors = require("./util.js").divisors;
var isPalindrome = require("./util.js").isPalindrome;
var Fibonacci = require("./generators.js").Fibonacci;

var CEIL = 1000000;

exports.preamble = ["Summing all numbers less than", CEIL, "which are",
    "palindromes in both base 10 and base 2."];

exports.solutions = {
  brute_force: function () {
    var total = 0;
    for (var i = 1; i < CEIL; i++) {
      if (isPalindrome(i) && isPalindrome(i.toString(2))) {
        total += i;
      }
    }
    return total;
  }
};
