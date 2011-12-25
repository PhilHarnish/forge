/**
 * Wrapper for `always` client.
 *
 * Launches processes needed to run:
 * - A background 'daemon' to route traffic (if none discovered)
 * - A background 'server' to serve files to test runners
 * - A client to negotiate the requests
 */

process.chdir(__dirname);
require.paths.push('../../src', '../../third_party');

var http = require('http'),
    client = require('./client.js'),
    master = require('./master.js'),
    server = require('./server.js');

client.start();
master.start();
server.start();



setInterval(function () {
  // Simulate a request from client to daemon.
  client.test("TaskTest");
}, 5000);



