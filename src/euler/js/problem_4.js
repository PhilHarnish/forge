var _ = require("../../../third_party/underscore/underscore.js")._;
var isPalindrome = require("./util.js").isPalindrome;

var MIN = 100;
var MAX = 999;

exports.preamble = ["Finding the largest palindrome from the product of two",
  "numbers between", MIN, "and", MAX + "."];

exports.solutions = {
  brute_force: function () {
    var a = MAX;
    var best = 404;
    while (a > MIN) {
      var offset = 0;
      while (offset <= MAX - a) {
        var b = MAX - offset;
        if (isPalindrome(a * b) && a * b > best) {
          best = a * b;
        }
        offset++;
      }
      a--;
    }
    return best;
  }
};
