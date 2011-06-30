var _ = require("../../../third_party/underscore/underscore.js")._;

var MULTIPLES = [3, 5];
var CEIL = 1000;

exports.preamble = ["Finding the sum of all the multiples of", MULTIPLES.join(" or "),
    "below", CEIL + "."];
exports.solutions = {
  brute_force: function () {
    var sum = 0;
    for (var i = 0; i < CEIL; i++) {
      var multiple = false;
      _(MULTIPLES).each(function(j) {
        if ((i % j) == 0) {
          multiple = true;
        }
      });
      if (multiple) {
        sum += i;
      }
    }
    return sum;
  },

  scan_multiples: function () {
    var sum = 0;
    var added = {};
    _(MULTIPLES).each(function(m) {
      for (var i = m; i < CEIL; i += m) {
        if (!(i in added)) {
          added[i] = true;
          sum += i;
        }
      }
    });
    return sum;
  }

  /**
   * TODO: a solution in O(num_multiples) time should be possible.
   * Calculate the sum of all multiples between two values. Then subtract
   * pairwise multiples (from over counting). Re-add any 3-way multiples (from
   * over subtracting). Etc.
   */
};
