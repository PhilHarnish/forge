
process.chdir(__dirname);
require.paths.push("../third_party/", "../src/", "../");

var util;
try {
  util = require("util");
} catch (e) {
  util = require("sys");
}

var j = require("jasmine-node/lib/jasmine-node"),
    TerminalReporter = require("jasmine-node/lib/jasmine-node/reporter").
        TerminalReporter;

function removeJasmineFrames(text) {
  var lines = [];
  text.split(/\n/).forEach(function(line) {
    if (line.indexOf("jasmine-2.0.0.rc1.js") == -1) {
      lines.push(line);
    }
  });
  return lines.join("\n");
}

exports.resetJasmineEnv = function () {
  jasmine.currentEnv_ = new jasmine.Env();
  jasmine.getEnv().addReporter(new TerminalReporter({
      print: util.print,
      stackFilter: removeJasmineFrames
  }));
};
exports.jasmine = jasmine;

// TODO(philharnish): Load angular as needed.
var jsdom = require("jsdom");
var fs = require("fs");
var src = fs.readFileSync("../third_party/angular.js/build/angular.js").
    toString();

jsdom.env({
  html: "<html><head></head><body></body></html>",
  src: [src],
  done: function (errors, window) {
    // Hacky way to define `angular`.
    global.angular = window.angular;
    jasmine.getEnv().execute();
  }
});
