var _ = require("../../../third_party/underscore/underscore.js")._;
var Primes = require("./generators.js").Primes;

var DATA = [
  "75".split(" "),
  "95 64".split(" "),
  "17 47 82".split(" "),
  "18 35 87 10".split(" "),
  "20 04 82 47 65".split(" "),
  "19 01 23 75 03 34".split(" "),
  "88 02 77 73 07 63 67".split(" "),
  "99 65 04 28 06 16 70 92".split(" "),
  "41 41 26 56 83 40 80 70 33".split(" "),
  "41 48 72 33 47 32 37 16 94 29".split(" "),
  "53 71 44 65 25 43 91 52 97 51 14".split(" "),
  "70 11 33 28 77 73 17 78 39 68 17 57".split(" "),
  "91 71 52 38 17 14 91 43 58 50 27 29 48".split(" "),
  "63 66 04 68 89 53 67 30 73 16 69 87 40 31".split(" "),
  "04 62 98 27 23 09 70 98 73 93 38 53 60 04 23".split(" ")];

/*
DATA = [
  "3".split(" "),
  "7 4".split(" "),
  "2 4 6".split(" "),
  "8 5 9 3".split(" ")];
*/

exports.preamble = ["Finding largest sum through a pyramid."];

exports.solutions = {
  brute_force: function (data) {
    data = data || DATA;
    var cache = [];
    var dir = [];
    _(data).each(function () {
      cache.push([]);
      dir.push([]);
    });
    var crawl = function (x, y) {
      if (cache[x][y]) {
        return cache[x][y];
      }
      var total = Number(data[y][x]);
      if (y + 1 < cache.length) {
        var left = crawl(x, y + 1);
        var right = crawl(x + 1, y + 1);
        dir[y][x] = left > right ? 0 : 1;
        total += Math.max(crawl(x, y + 1), crawl(x + 1, y + 1));
      }
      cache[x][y] = total;
      return total;
    };

    var x = 0;
    /*
    crawl(0, 0);
    console.log(_(dir).map(function (i, j) {
      var oldX = x;
      x += i[x];
      return DATA[j][oldX];
    }));
    */
    return crawl(0, 0);
  }
};
