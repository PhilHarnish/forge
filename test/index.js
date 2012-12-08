
process.chdir(__dirname);
require.paths.push("../third_party/", "../src/", "../");

var util;
try {
  util = require("util");
} catch (e) {
  util = require("sys");
}

var j = require("jasmine-node/lib/jasmine-node");
var TerminalReporter = require("jasmine-node/lib/jasmine-node/reporter").
        TerminalReporter;
var JasmineSink = require("./JasmineSink.js");

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
  jasmine.currentEnv_.beforeEach(function () {
    this.addMatchers(JasmineSink.matchers);
  });
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

global.register = function(name) {
  // Save original angular module function and replace it.
  var originalModuleFn = angular.module;
  angular.module = loadModule;
  // Load the module requested.
  loadScript(name);
  angular.module = originalModuleFn;
  // Register module with angular.mock.
  return angular.mock.module(name);

  function loadModule(name, requires, configFn) {
    var loadedModule = originalModuleFn(name, requires, configFn);
    if (requires) {
      // Load all dependent scripts.
      for (var i = 0; i < requires.length; i++) {
        if (requires[i].slice(-3) == ".js") {
          loadScript(requires[i]);
        }
      }
    }
    return loadedModule;
  }

  function loadScript(src) {
    require(src);
  }
};
