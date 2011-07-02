var _ = require("../../../third_party/underscore/underscore.js")._;
var Primes = require("./generators.js").Primes;

var SIZE = 20;

exports.preamble = ["Finding all routes in a grid of", SIZE + "x" + SIZE + "."];

exports.solutions = {
  brute_force: function () {
    var cache = {};
    cache[SIZE + "x" + SIZE] = 1;
    var crawl = function (x, y) {
      var key = x + "x" + y;
      if (cache[key]) {
        return cache[key];
      }
      var subtotal = 0;
      if (x < SIZE) {
        subtotal += crawl(x + 1, y);
      }
      if (y < SIZE) {
        subtotal += crawl(x, y + 1);
      }
      cache[key] = subtotal;
      return subtotal;
    };
    return crawl(0, 0);
  }
};
