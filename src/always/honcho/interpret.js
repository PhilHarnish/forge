var crypto = require('crypto'),
    fs = require("fs"),

    mime = require("third_party/node-mime/mime.js");

// Takes any text following "." or "/", whichever comes last. Else "".
var _EXTENSION_REGEX = /[^./]*$/;

// Map of lists, keyed on accept type. List organized in MRU order.
var _interpreterTypeList = {};
var _identifierTypeList = {};

// _identifyCount monotonically increases each time identify() is called.
var _identifyCount = 0;

var _parseAcceptType = function(acceptType) {
  var parts = acceptType.split(";");
  var type = parts.shift();
  // Set special q parameter to default value of 1. May be overridden.
  var result = {
    q: 1
  };
  while (parts.length) {
    var kvp = parts.pop().split("=");
    var key = kvp[0];
    var value = kvp[1];
    result[key] = isNaN(value) ? value : Number(value);
  }
  // Set type last to prevent parameters from overriding.
  result.type = type.replace("*/*", "").replace("/*", "");
  return result;
};

var _makeIdentifierLatch = function (identifier) {
  var lastIdentified = 0;
  return function () {
    if (lastIdentified < _identifyCount) {
      return identifier.apply(null, arguments);
    }
    lastIdentified = _identifyCount;
  };
};

exports.identifier = function (type, identifier) {
  // Add identifier for type.
  var latchedIdentifier = _makeIdentifierLatch(identifier);
  _identifierTypeList[type] = {
    identifier: latchedIdentifier,
    _next: _identifierTypeList[type]
  };
};

exports.identify = function (fileName, contents, typeHint) {
  _identifyCount++;
  var initialType = typeHint ||
      _parseAcceptType(mime.lookup(fileName,
          _EXTENSION_REGEX.exec(fileName)[0]));
  var identifyTypeStack = [
    "*",
    initialType.type
  ];
  while (identifyTypeStack.length) {
    var type = identifyTypeStack.pop();
    var iterator = _identifierTypeList[type];
    var last = null;
    while (iterator) {
      var result = iterator.identifier(fileName, contents, initialType.type);
      if (result) {
        if (last) {
          // A non-null 'last' implies we've moved away from head and the
          // new Most Recently Used parser is 'iterator'.
          last._next = iterator._next;
          iterator._next = _identifierTypeList[type];
          _identifierTypeList[type] = iterator;
        }
        return _parseAcceptType(result);
      }
      last = iterator;
      iterator = iterator._next;
    }
  }
  // Return what we learned from fileName alone.
  return initialType;
};

exports.interpreter = function (acceptListString, interpreter) {
  var acceptList = acceptListString.split(",");
  while (acceptList.length) {
    var acceptType = _parseAcceptType(acceptList.pop());
    var type = acceptType.type;
    // Add to head.
    _interpreterTypeList[type] = {
      accept: acceptType,
      interpreter: interpreter,
      _next: _interpreterTypeList[type]
    };
  }
};

/**
 * Given a goal, returns the most similar between left and right.
 *
 * Order of comparison:
 * 0) Return left if right is ineligible. Else,
 * 1) Return side with higher willingness to interpret ("q"). Else,
 * 2) Return side with most common prefix characters. Else,
 * 3) Return side with most matching keys. Else,
 *
 * @param goalAccept
 * @param left
 * @param right
 */
var _findMostEligible = function (goalAccept, left, right) {
  var rightAccept = right.accept;
  var rightPrefixLength = goalAccept.type.indexOf(rightAccept.type) == 0 ?
      rightAccept.type.length : 0;
  if (!rightPrefixLength) {
    return left;
  }
  var rightKeyCount = 0;
  var key;
  for (key in rightAccept) {
    if (key != "q" && key != "type") {
      // Verify each key in right is in goalAccept. This ensures, for
      // example, that "nodejs=1" interpreters are only paired with
      // nodejs goals.
      if (key in goalAccept && goalAccept[key] == right[key]) {
        rightKeyCount++;
      } else {
        return left;
      }
    }
  }
  // TODO: Cache left's score?
  var leftAccept = left.accept;
  var leftPrefixLength = goalAccept.type.indexOf(leftAccept.type) == 0 ?
      leftAccept.type.length : 0;
  if (leftPrefixLength > rightPrefixLength) {
    return left;
  } else if (rightPrefixLength > leftPrefixLength) {
    return right;
  }
  var leftKeyCount = 0;
  for (key in leftAccept) {
    if (key != "q" && key != "type") {
      // Assume keys in left already match since they initially match
      // and each subsequent candidate already passed check.
      leftKeyCount++;
    }
  }
  if (rightKeyCount > leftKeyCount) {
    return right;
  }
  return left;
};

exports.source = function (fileName, contents, typeHint) {
  var type = exports.identify(fileName, contents, typeHint);
  var interpreterTypeStack = [
    "",
    type.type.split("/")[0], // TODO: de-dupe
    type.type
  ];
  var best = _initialInterpreter;
  while (interpreterTypeStack.length && best.accept.q < 1) {
    var group = interpreterTypeStack.pop();
    var iterator = _interpreterTypeList[group];
    while (iterator) {
      best = _findMostEligible(type, best, iterator);
      iterator = iterator._next;
    }
  }
  return best.interpreter(fileName, contents, type);
};

exports.baseInterpreter = function (fileName, contents, type) {
  var shaHash = crypto.createHash("sha1");
  shaHash.update(contents);
  return {
    digest: shaHash.digest("hex"),
    fileName: fileName,
    type: type
  };
};

var _initialInterpreter = {
  accept: _parseAcceptType("*/*;q=0.1"),
  interpreter: exports.baseInterpreter
};

/**
 * Load identifiers and interpreters.
 */
(function (map) {
  for (var job in map) {
    var path = __dirname + "/" + job;
    var files = fs.readdirSync(path);
    for (var i = 0; i < files.length; i++) {
      var module = require(path + "/" + files[i]);
      for (var type in module) {
        // Eg: call exports.identifier("text/javascript", fn);
        map[job](type, module[type]);
      }
    }
  }
})({
  identifiers: exports.identifier,
  interpreters: exports.interpreter
});
