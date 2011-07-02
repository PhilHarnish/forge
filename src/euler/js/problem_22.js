var fs = require("fs");
var path = require("path");
var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;
var divisors = require("./util.js").divisors;
var Fibonacci = require("./generators.js").Fibonacci;

exports.preamble = ["Finding the total 'name score' for names.txt."];

var EULER_TOP = __filename.split("/euler/")[0] + "/euler/";
var NAMES = fs.readFileSync(path.join(EULER_TOP,
                                      "data/names.txt"), 'ascii').split('","');
// Fix first and last names which have " in them still.
NAMES[0] = NAMES[0].substr(1);
NAMES[NAMES.length - 1] = NAMES[NAMES.length - 1].slice(0, -1);

exports.solutions = {
  brute_force: function () {
    var a = "A".charCodeAt(0) - 1;
    NAMES.sort();
    return _(NAMES).reduce(function (memo, name, i) {
      var subtotal = 0;
      for (var l = name.length - 1; l >= 0; l--) {
        subtotal += name.charCodeAt(l) - a;
      }
      return memo + subtotal * (i + 1);
    }, 0);
  }
};
