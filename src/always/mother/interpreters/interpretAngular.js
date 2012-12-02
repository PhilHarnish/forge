var baseInterpreter = require("always/mother/interpret.js").
    baseInterpreter;

_ANGULAR_DEPS = /angular.module\(['"][^'"]+['"], (\[[^\]]+\])\)/g;
var _interpretAngularJs = function (resource, type) {
  var contents = resource.contents;
  var interpretation = baseInterpreter(resource, type);
  interpretation.deps = [];
  var match;
  console.log("Interpreting:", resource.fileName);
  do {
    match = _ANGULAR_DEPS.exec(contents);
    if (match && match.length > 1) {
      interpretation.deps.push.apply(interpretation.deps, eval(match[1]));
    }
  } while (match);
  console.log(interpretation.deps);
  return interpretation;
};

module.exports = {
  // Accept JS identified as AngularJS
  "application/javascript;angularjs=1": _interpretAngularJs,
  // Tolerate ordinary JavaScript at 80% "quality".
  "application/javascript;q=.8": _interpretAngularJs
};
