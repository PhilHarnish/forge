var _ = require("../../../third_party/underscore/underscore.js")._;
var factors = require("./util.js").factors;

var NUM = 600851475143;
//var NUM = 13195;
//var NUM = 15;

exports.preamble = ["Finding the largest prime factor in", NUM + "."];

exports.solutions = {
  brute_force: function () {
    return factors(NUM).pop();
  }
};
