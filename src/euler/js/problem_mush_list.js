var _ = require("../../../third_party/underscore/underscore.js")._;

var ALPHA_MUSH = 2;
var BETA_MUSH = 0;
var SAFE = 1;
var TRUSTED = 4;
var LIST_SIZE = 3;
var SHIP_SIZE = 16;

exports.preamble = ["Calculate probability of mush identification with",
  ALPHA_MUSH, "alpha mush,", BETA_MUSH, "beta mush", SAFE, "known clean",
  TRUSTED, "probably clean and a list with", LIST_SIZE, "names."];

/**
 * Result:
{
 '2 mush 1 safe 1 trusted': 4,
 '2 mush 1 safe 1 other': 9,
 '2 mush 2 trusted': 6,
 '2 mush 1 trusted 1 other': 36,
 '2 mush 2 other': 36,
 '1 mush 1 safe 2 trusted': 6,
 '1 mush 1 safe 1 trusted 1 other': 36,
 '1 mush 1 safe 2 other': 36,
 '1 mush 3 trusted': 4,
 '1 mush 2 trusted 1 other': 54,
 '1 mush 1 trusted 2 other': 144,
 '1 mush 3 other': 84
}
 */

exports.solutions = {
  brute_force: function () {
    var list = [0];
    var counts = {};
    var recurse = function(start) {
      if (list.length < LIST_SIZE) {
        for (var i = start; i < SHIP_SIZE; i++) {
          list.push(i);
          recurse(i + 1);
          list.pop();
        }
      } else {
        var key = getKey(list);
        counts[key] = (counts[key] || 0) + 1;
        //console.log(list, key);
      }
    };
    recurse(1);
    for (var type in counts) {
      console.log(type);
      console.log(counts[type]);
    }
    return counts;
  }
};

var getKey = function(list) {
  var mush = 0;
  var safe = 0;
  var trusted = 0;
  var other = 0;
  for (var i = 0; i < list.length; i++) {
    if (list[i] < ALPHA_MUSH + BETA_MUSH) {
      mush++;
    } else if (list[i] < ALPHA_MUSH + BETA_MUSH + SAFE) {
      safe++;
    } else if (list[i] < ALPHA_MUSH + BETA_MUSH + SAFE + TRUSTED) {
      trusted++;
    } else {
      other++;
    }
  }
  var key = [mush, 'mush'];
  if (safe) {
    key.push(safe, 'safe');
  }
  if (trusted) {
    key.push(trusted, 'trusted');
  }
  if (other) {
    key.push(other, 'other');
  }
  return key.join(' ');
};
