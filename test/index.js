
process.chdir(__dirname);
require.paths.push("../third_party/", "../src/", "../");

var util;
try {
  util = require("util");
} catch (e) {
  util = require("sys");
}

var jasmine = require("jasmine-node/lib/jasmine-node"),
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

jasmineEnv = jasmine.getEnv();
jasmineEnv.addReporter(new TerminalReporter({
    print: util.print,
    stackFilter: removeJasmineFrames
}));

// Hacky way to execute tests after they are all defined.
setTimeout(function () {
  jasmineEnv.execute();
}, 0);
