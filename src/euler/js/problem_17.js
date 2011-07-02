var _ = require("../../../third_party/underscore/underscore.js")._;
var bc = require("./bc.js").bc;
var divisors = require("./util.js").divisors;
var Fibonacci = require("./generators.js").Fibonacci;

var CEIL = 1000;

var DICT = {
  "1": "one",
  "2": "two",
  "3": "three",
  "4": "four",
  "5": "five",
  "6": "six",
  "7": "seven",
  "8": "eight",
  "9": "nine",
  "10": "ten",
  "11": "eleven",
  "12": "twelve",
  "13": "thirteen",
  "14": "fourteen",
  "15": "fifteen",
  "16": "sixteen",
  "17": "seventeen",
  "18": "eighteen",
  "19": "nineteen",
  "20": "twenty",
  "30": "thirty",
  "40": "forty",
  "50": "fifty",
  "60": "sixty",
  "70": "seventy",
  "80": "eighty",
  "90": "ninety"
};

exports.preamble = ["Finding the sum of all letters in the numbers 1.." + CEIL];

exports.solutions = {
  brute_force: function () {
    var total = 0;
    for (var i = 1; i <= CEIL; i++) {
      var num = i;
      var str = "";
      var idx = Math.floor(num / 1000);
      if (idx in DICT) {
        str += DICT[idx] + "thousand";
        num %= 1000;
      }
      idx = Math.floor(num / 100);
      if (idx in DICT) {
        str += DICT[idx] + "hundred";
        num %= 100;
      }
      if (str && num) {
        str += "and";
      }
      if (num in DICT) {
        str += DICT[num];
        num = 0;
      }
      idx = Math.floor(num / 10) * 10;
      if (idx in DICT) {
        str += DICT[idx];
        num %= 10;
      }
      if (num in DICT) {
        str += DICT[num];
        num = 0;
      }
      total += str.length;
    }
    return total;
  }
};
