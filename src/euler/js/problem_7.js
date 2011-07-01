var _ = require("../../../third_party/underscore/underscore.js")._;
var Primes = require("./generators.js").Primes;

var COUNT = 10001;

exports.preamble = ["Finding prime #" + COUNT];

exports.solutions = {
  brute_force: function () {
    p = new Primes;
    c = COUNT;
    while (--COUNT) {
      p.next();
    }
    return p.next();
  }
};
