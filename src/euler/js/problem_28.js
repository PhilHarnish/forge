var fs = require("fs");
var path = require("path");
var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;
var divisors = require("./util.js").divisors;
var Fibonacci = require("./generators.js").Fibonacci;

var SIZE = 1001;

exports.preamble = ["Summing the diagnal in a", SIZE + "x" + SIZE, "spiral."];

exports.solutions = {
  brute_force: function () {
    var total = 1;
    var i = 1;
    var len = 2;
    while (len < SIZE) {
      for (var times = 0; times < 4; times++) {
        for (var edge = 0; edge < len; edge++) {
          i++;
        }
        total += i;
      }
      len += 2;
    }
    return total;
  }
};
