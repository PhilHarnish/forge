var fs = require("fs");
var path = require("path");
var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;
var divisors = require("./util.js").divisors;
var Fibonacci = require("./generators.js").Fibonacci;

var MAX_BASE = 100;
var MAX_EXPONENT = 100;

exports.preamble = ["Counting distinct terms for a^b where a = 2.." + MAX_BASE,
    "and b = 2.." + MAX_EXPONENT + "."];

exports.solutions = {
  brute_force: function () {
    var terms = [];
    for (var base = 2; base <= MAX_BASE; base++) {
      for (var exponent = 2; exponent <= MAX_BASE; exponent++) {
        terms.push(bc.valueOf(bc.pow(bc(base), exponent)));
      }
    }
    terms = _(terms.sort()).uniq(true);
    return terms.length;
  }
};
