var _ = require("third_party/underscore/underscore.js");

module.exports = {
  matchers: {
    toBeEmpty: function () {
      return _.isEmpty(this.actual);
    },
    toHave: function (expected) {
      return (expected in this.actual) ||
          objectIsSubset(this.actual, expected);
    }
  }
};

function objectIsSubset(a, b) {
  if (a == b) {
    // Trivial case.
    return true;
  }
  var hasEqualKeys = false;
  for (var key in b) {
    // Look for properties which b has but a doesn't.
    if (b.hasOwnProperty(key)) {
      if (!a.hasOwnProperty(key) || !objectIsSubset(a[key], b[key])) {
        return false;
      }
      hasEqualKeys = true;
    }
  }
  return hasEqualKeys;
}
