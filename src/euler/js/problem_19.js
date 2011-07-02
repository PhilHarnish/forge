var fs = require("fs");
var path = require("path");
var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;
var divisors = require("./util.js").divisors;
var Fibonacci = require("./generators.js").Fibonacci;

var START = new Date(1901, 1, 1);
var END = new Date(2000, 12, 31);

exports.preamble = ["Finding the total first-Sundays between", START, "and",
  END, "."];

exports.solutions = {
  brute_force: function () {
    var today = START;
    var total = 0;
    while (today.getTime() < END.getTime()) {
      if (today.getDay() == 0) {
        total++;
      }
      today.setMonth(today.getMonth() + 1);
    }
    return total;
  }
};
