var baseInterpreter = require("always/mother/interpret.js").
    baseInterpreter;

_REQUIRE_REGEXP = /require\(['"]([^'"]+)['"]\)/g;
var _interpretNodeJs = function (resource, type) {
  var contents = resource.contents;
  var interpretation = baseInterpreter(resource, type);
  interpretation.deps = [];
  var match;
  do {
    match = _REQUIRE_REGEXP.exec(contents);
    if (match && match.length > 1) {
      interpretation.deps.push(match[1]);
    }
  } while (match);
  return interpretation;
};

module.exports = {
  // Happily accept JS identified as NodeJS
  "application/javascript;nodejs=1": _interpretNodeJs,
  // Tolerate ordinary JavaScript at 80% "quality".
  "application/javascript;q=.8": _interpretNodeJs
};