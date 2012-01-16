var _deps = {
  // Application.
  "views/SignIn.js": {
    deps: [
      "events/Event.js",
      "ui/CheckBox.js",
      "ui/TextField.js",
      "ui/SubmitButton.js"
    ]
  },

  // Core.
  "events/Event.js": {
    deps: []
  },
  "events/EventDispatcher.js": {
    deps: [
      "events/Event.js",
      "events/IEventDispatcher.js"
    ]
  },
  "events/IEventDispatcher.js": {
    deps: []
  },
  "ui/Button.js": {
    deps: [
      "events/Event.js",
      "ui/UiElement.js"
    ]
  },
  "ui/CheckBox.js": {
    deps: [
      "events/Event.js",
      "ui/UiElement.js"
    ]
  },
  "ui/DisplayElement.js": {
    deps: []
  },
  "ui/SubmitButton.js": {
    deps: [
      "ui/Button.js"
    ]
  },
  "ui/TextField.js": {
    deps: [
      "events/Event.js",
      "ui/UiElement.js"
    ]
  },
  "ui/UiElement.js": {
    deps: [
      "events/EventDispatcher.js",
      "ui/DisplayElement.js"
    ]
  },

  // Tests.
  "tests/Test.js": {
    deps: [
      "events/EventDispatcher.js"
    ]
  },
  "tests/TestRunner.js": {
    deps: [
      "events/Event.js",
      "tests/Test.js"
    ]
  },
  "tests/events/TestEvent.js": {
    deps: [
      "events/Event.js",
      "tests/Test.js"
    ]
  },
  "tests/events/TestEventDispatcher.js": {
    deps: [
      "events/Event.js",
      "events/EventDispatcher.js",
      "tests/Test.js"
    ]
  },
  "tests/ui/TestButton.js": {
    deps: [
      "events/Event.js",
      "ui/Button.js",
      "tests/Test.js"
    ]
  },
  "tests/ui/TestCheckBox.js": {
    deps: [
      "events/Event.js",
      "ui/CheckBox.js",
      "tests/Test.js"
    ]
  },
  "tests/ui/TestSubmitButton.js": {
    deps: [
      "events/Event.js",
      "ui/SubmitButton.js",
      "tests/Test.js"
    ]
  },
  "tests/ui/TestTextField.js": {
    deps: [
      "events/Event.js",
      "ui/TextField.js",
      "tests/Test.js"
    ]
  },
  "tests/ui/TestUiElement.js": {
    deps: [
      "events/Event.js",
      "ui/UiElement.js",
      "tests/Test.js"
    ]
  }
};

// Populate parents.
(function (deps) {
  for (var file in deps) {
    var list = deps[file].deps;
    for (var i = 0; i < list.length; i++) {
      var target = deps[list[i]];
      if (!target.parents) {
        target.parents = [file];
      } else {
        // Note: Dupe parents are impossible since keys in `deps` don't repeat.
        target.parents.push(file);
      }
    }
  }
})(_deps);

/**
 * Returns a shallow copy of local _deps in file => [deps] format..
 * @param filter (optional) specify file to retrieve deps for.
 */
exports.getDeps = function (filter) {
  var result = {};
  if (filter in _deps) {
    result[filter] = _deps[filter].deps.concat();
  } else {
    for (var key in _deps) {
      if (!filter || filter.match(key)) {
        result[key] = _deps[key].deps.concat()
      }
    }
  }
  return result;
};

// Reverse lookup of _deps.
var _visit = function (data, key, file, pre, post, visited) {
  if (!(file in visited)) {
    pre.push(file);
    visited[file] = true;
    for (var sub in data[file][key]) {
      _visit(data, key, data[file][key][sub], pre, post, visited);
    }
    post.push(file);
  }
};

exports.getAffected = function (file) {
  var affected = [];
  _visit(_deps, "parents", file, affected, [], {});
  return affected;
};

exports.getImportOrder = function (file) {
  var imported = [];
  _visit(_deps, "deps", file, imported, [], {});
  return imported;
};

exports.getExecuteOrder = function (file) {
  var executed = [];
  _visit(_deps, "deps", file, [], executed, {});
  return executed;
};

var FILE_TEMPLATE = [
  "module.exports = {",
  "  name: \"$FILE_PATH\"",
  "};",
  "",
  "if (global.importOrder) {",
  "  global.importOrder.push(module.exports.name);",
  "}",
  "",
  "$REQUIRES",
  "",
  "if (global.executeOrder) {",
  "  global.executeOrder.push(module.exports.name);",
  "}",
  ""
];
var REQUIRE_TEMPLATE = "var $REQUIRE_ID = require(\"$FILE_PATH\");";
var REQUIRE_ID_REGEXP = /\/([^/]+).js/;

/**
 * Returns the contents of a file given filePathString.
 * @param filePathString
 */
exports.getFileContents = function (filePathString) {
  if (filePathString in _deps) {
    var target = _deps[filePathString];
    var requires = [];
    for (var depNum in target.deps) {
      var depPathNameString = target.deps[depNum];
      var requireIdString = REQUIRE_ID_REGEXP.exec(depPathNameString)[1];
      requires.push(
          REQUIRE_TEMPLATE.replace("$REQUIRE_ID", requireIdString).
              replace("$FILE_PATH", depPathNameString)
      );
    }
    var requiresString = requires.join("\n");
    return FILE_TEMPLATE.join("\n").
        replace("$REQUIRES", requiresString).
        replace("$FILE_PATH", filePathString);
  }
  return "";
};
