
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
  jasmine.currentEnv_.beforeEach(global.angular.mock.before);
  jasmine.currentEnv_.afterEach(global.angular.mock.after);
  jasmine.currentEnv_.it = function(description, func) {
    jasmine.Env.prototype.it.call(this, description, inject(func));
  };
  jasmine.getEnv().addReporter(new TerminalReporter({
      print: util.print,
      stackFilter: removeJasmineFrames
  }));
};
exports.jasmine = jasmine;

// TODO(philharnish): Load angular as needed.
if (!global.angular) {
  var jsdom = require("jsdom");
  jsdom.env({
    html: "<html><head>" +
        "<base href='" + __dirname + "'>" +
        "</head><body></body></html>",
    scripts: [
      "test/angularbootstrap.js",
      "third_party/angular.js/build/angular.js",
      "third_party/angular.js/build/angular-resource.js",
      "third_party/angular.js/build/angular-mocks.js"],
    src: [],
    done: function (errors, window) {
      // Hacky way to define `angular`.
      for (var key in window) {
        if (window.hasOwnProperty(key) && !global.hasOwnProperty(key)) {
          global[key] = window[key];
        }
      }
      jasmine.getEnv().execute();
    }
  });
}
