var fs = require("fs");
var path = require("path");
var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;
var divisors = require("./util.js").divisors;
var Fibonacci = require("./generators.js").Fibonacci;

var EULER_TOP = __filename.split("/euler/")[0] + "/euler/";
var TRIANGLE = fs.readFileSync(
    path.join(EULER_TOP, "data/triangle.txt"), 'ascii').split("\n");
TRIANGLE = _(TRIANGLE).map(function (line) {
  return line.split(" ");
});
TRIANGLE.pop();

exports.preamble = ["Finding largest sum through triangle.txt."];

exports.solutions = {
  brute_force: function () {
    return require("./problem_18.js").solutions.brute_force(TRIANGLE);
  }
};
