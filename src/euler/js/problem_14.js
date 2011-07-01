var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;

var CEIL = 1000000;

exports.preamble = ["Finding the longest (Collatz Problem) sequence under",
    CEIL + "."];

exports.solutions = {
  brute_force: function () {
    // Insert dummy value and then 1. 1 based index is convenient.
    var cache = [NaN, 1];
    // Seed cache
    var l = cache.length;
    var max = CEIL / 10;
    while (l++ < max) {
      cache.push(0);
    }
    var collatz = function (n) {
      if (n <= max && cache[n]) {
        return cache[n];
      }
      var depth = (n % 2 == 0) ? collatz(n / 2) : collatz(3 * n + 1);
      depth++;
      if (n < max) {
        cache[n] = depth;
      }
      return depth;
    };
    // Compute every value up to CEIL
    var largestSeries = 0;
    var largestStart = 0;
    for (var i = 1; i <= CEIL; i++) {
      var series = collatz(i);
      if (series > largestSeries) {
        largestSeries = series;
        largestStart = i;
      }
    }
    return largestStart;
  }
};
