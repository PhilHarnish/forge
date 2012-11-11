var _ = require("../../../third_party/underscore/underscore.js")._;

/*
 * Ruby VALUEs
 * 0b...xxxxxxx1 fixnum
 * 0b...00000010 true
 * 0b...00000110 undef
 * 0b...xxxx1110 symbol
 *
 * 0b...00000x00 RTEST
 * 0b...00000000 false
 * 0b...00000100 nil
 *
 * 0b...xxxxxx00 BUILTIN (nb: x > 1)
 */

var bc = function (n) {
  return bc._scrub(n);
};

_.extend(bc, {
  TRUNCATE: Infinity,
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
    var digits = Math.min(Math.max(a.length, b.length), bc.TRUNCATE);
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
    // a.length > b.length
    var aLength = a.length;
    var bLength = Math.min(b.length, bc.TRUNCATE);
    var row;
    var offset = 0;
    var remainder = 0;
    // For each digit in b...
    for (var bDigit = 0; bDigit < bLength; bDigit++) {
      row = bc._pad([], offset);
      // Multiply every digit in a...
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
  },
  pow: function(n, p) {
    var r = bc(1);
    while (p > 1) {
      var l = Math.floor(Math.log(p) / Math.log(2));
      p -= Math.pow(2, l);
      var m = _(n).clone();
      while (l--) {
        m = bc.mult(m, m);
      }
      r = bc.mult(r, m);
    }
    if (p) {
      r = bc.mult(r, n);
    }
    return r;
  }
});

exports.bc = bc;
