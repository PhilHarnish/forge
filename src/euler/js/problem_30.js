var fs = require("fs");
var path = require("path");
var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;
var divisors = require("./util.js").divisors;
var Fibonacci = require("./generators.js").Fibonacci;

var POW = 5;

exports.preamble = ["Find the sum of all numbers AB...Z = A^" + POW, "+ B^" +
  POW, "+ ... + Z^" + POW];

exports.solutions = {
  brute_force: function () {
    var total = 0;
    var i = 1;
    // What is the real max??
    var max = Math.pow(10, POW + 1);
    var test = function(n) {
      var target = n;
      var total = 0;
      while (n) {
        var digit = n % 10;
        n = Math.floor(n / 10);
        total += Math.pow(digit, POW);
      }
      return total == target;
    };
    while (i++ < max) {
      if (test(i)) {
        console.log("Found candidate", i);
        total += i;
      }
    }
    return total;
  }
};
