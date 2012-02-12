require.paths.push("src", "third_party");
var Mother = require("always/mother/Mother.js");

var mother = new Mother();
mother.loadDir(process.cwd());

var test = require(process.cwd() + "/test");

var id = 0;
var testLoop = function () {
  test.resetJasmineEnv();
  mother.test("...");
  // TODO: Pretty gross.
  if (test.jasmine.getEnv().currentRunner_.specs().length) {
    test.jasmine.getEnv().execute();
  }
};
var warmupTimeout;
var testLoopWarmup = function () {
  clearTimeout(warmupTimeout);
  warmupTimeout = setTimeout(testLoop, 50);
};
mother.onFileChange(testLoopWarmup);

/**
 * Wrapper for `always` client.
 *
 * Launches processes needed to run:
 * - A background "daemon" to route traffic (if none discovered)
 * - A background "server" to serve files to test runners
 * - A client to negotiate the requests
 */

/*
 The following creates client/master/server daemons to execute tests.
 *
process.chdir(__dirname);
require.paths.push("../../src", "../../third_party");

var http = require("http"),
    client = require("./client.js"),
    master = require("./master.js"),
    server = require("./server.js");

client.start();
master.start();
server.start();



setInterval(function () {
  // Simulate a request from client to daemon.
  client.test("TaskTest");
}, 5000);

// */


