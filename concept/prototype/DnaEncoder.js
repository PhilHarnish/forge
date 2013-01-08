angular.module("DnaEncoder.js", []).
    factory("DnaEncoder", function() {
      return DnaEncoder;
    });

var BASE64 = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ" +
    "abcdefghijklmnopqrstuvwxyz" +
    "0123456789-_").split("");

function DnaEncoder() {
  this.model = {};
  this.parsed = "";
}

DnaEncoder.LINE_REGEX = /(\s*)(\d+)(?:: (.+))?$/;

DnaEncoder.prototype.setModel = function(model) {
  this.model = model;
};

DnaEncoder.prototype.setValue = function(str) {
  var lines = str.split("\n");
  var frame;
  var stack = [];
  var depth = -1;
  var node = {};
  for (var i = 0; i < lines.length; i++) {
    var parsed = DnaEncoder.LINE_REGEX.exec(lines[i]);
    if (!parsed) {
      console.log("ERROR ON LINE", i, ":", lines[i]);
      return;
    }
    var indentation = parsed[1].length;
    var value = Number(parsed[2]);
    var name = parsed[3];
    if (indentation == depth) {
      // Same level.
    } else if (indentation == depth + 1) {
      // Indent.
      depth = indentation;
      frame = [];
      node.children = frame;
      stack[depth] = frame;
    } else if (indentation < depth) {
      // Finished with a level.
      depth = indentation;
      frame = stack[depth];
    } else {
      console.log("INDENTATION ERROR", i, ":", lines[i]);
      return;
    }
    node = {
      "value": value,
      "name": name,
      "children": []
    };
    frame.push(node);
  }
  this.parsed = stack[0];
};

DnaEncoder.prototype.getValue = function() {
  function recurse(value, result, depth) {
    for (var i = 0; i < value.length; i++) {
      var node = value[i];
      var name = node.name ? ": " + node.name : "";
      var indentation = new Array(depth + 1).join(" ");
      result.push(indentation + node.value + name);
      if (node.children.length) {
        recurse(node.children, result, depth + 1);
      }
    }
    return result;
  }
  return recurse(this.parsed, [], 0).join("\n");
};

DnaEncoder.prototype.getEncoding = function() {
  return this.getValue() + "Encoded!";
};

