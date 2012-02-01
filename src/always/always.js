require.paths.push("src", "third_party");
var Honcho = require("always/honcho/Honcho.js"),
    revolver = require("revolver/revolver.js");

var honcho = new Honcho();
honcho.loadDir(process.cwd());

var test = require(process.cwd() + "/test");

var id = 0;
var testLoop = function () {
  test.resetJasmineEnv();
  honcho.test("...");
  test.jasmine.getEnv().execute();
  // Rinse and repeat.
  setTimeout(testLoop, 5000);
};

setTimeout(testLoop, 5000);

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


