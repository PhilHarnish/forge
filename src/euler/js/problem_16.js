var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;

var POW = 1000;

exports.preamble = ["Finding the sum of the digits in 2^" + POW + "."];

exports.solutions = {
  brute_force: function () {
    var remaining = POW;
    var n = [1];
    while (remaining--) {
      n = bc.mult(n, [2])
    }
    var result = 0;
    while (n.length) {
      result += n.pop();
    }
    return result;
  }
};
