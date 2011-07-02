var _ = require("../../../third_party/underscore/underscore.js")._;

var bc = function (n) {
  return bc._scrub(n);
};

_.extend(bc, {
  _pad: function (n, size) {
    while (n.length < size) {
      n.push(0);
    }
    return n;
  },
  _scrub: function (n) {
    if (!n.split) {
      n = n.toString();
    }
    n = n.split('');
    var l = n.length;
    while (l--) {
      n[l] = Number(n[l]);
    }
    return n.reverse();
  },
  valueOf: function (n) {
    var copy = _(n).clone();
    return copy.reverse().join('');
  },
  sum: function (a, b) {
    result = [];

    var remainder = 0;
    var digits = Math.max(a.length, b.length);
    a = bc._pad(a, digits);
    b = bc._pad(b, digits);
    var digit = 0;
    while (digit < digits) {
      var subtotal = a[digit] + b[digit] + remainder;
      result.push(subtotal % 10);
      remainder = Math.floor(subtotal / 10);
      digit++;
    }
    while (remainder) {
      result.push(remainder);
      remainder = Math.floor(remainder / 10);
    }
    return result;
  },
  mult: function (a, b) {
    // aaaaa
    // * bbb
    var result = [];
    if (b.length > a.length) {
      var t = a;
      a = b;
      b = t;
    }
    var aLength = a.length;
    var bLength = b.length;
    var row;
    var offset = 0;
    var remainder = 0;
    for (var bDigit = 0; bDigit < bLength; bDigit++) {
      row = bc._pad([], offset);
      for (var aDigit = 0; aDigit < aLength; aDigit++) {
        var subtotal = a[aDigit] * b[bDigit] + remainder;
        row.push(subtotal % 10);
        remainder = Math.floor(subtotal / 10);
      }
      while (remainder) {
        row.push(remainder);
        remainder = Math.floor(remainder / 10);
      }
      result = bc.sum(result, row);
      offset++;
    }
    return result;
  }
});

exports.bc = bc;
