var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;

var NUM = 100;

exports.preamble = ["Sum the digits in " + NUM + "!"];

exports.solutions = {
  brute_force: function () {
    var m = 1;
    var n = [1];
    while (m++ < NUM) {
      n = bc.mult(bc(m), n);
    }
    var result = 0;
    while (n.length) {
      result += n.pop();
    }
    return result;
  }
};
