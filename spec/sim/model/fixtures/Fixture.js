var _ = require("underscore/underscore.js");

module.exports = function (fixtures) {
  var result;
  // Assign to "exports" to help IntelliJ find these definitions.
  exports = {
    "get": function () {
      var requested = [{}];
      for (var i = 0; i < arguments.length; i++) {
        var key = arguments[i];
        if (fixtures.hasOwnProperty(key)) {
          requested.push(fixtures[key]);
        } else {
          throw new TypeError("Object #<Object> has no key '" +
              key + "'");
        }
      }
      if (requested.length == 1) {
        requested.push(fixtures["default"]);
      }
      return _.extend.apply(requested, requested);
    }
  };
  result = exports;
  return exports;
};
