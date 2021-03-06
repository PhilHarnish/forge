
var fs = require("fs"),
    http = require("http"),
    master = require("always/master.js"),

    mime = require("node-mime/mime.js"),
    State = require("always/State.js"),
    Task = require("always/Task.js"),
    uuid = require("node-uuid/uuid.js");

server = false;

// Returns files which contain task masters and tasks

// TODO: centralized state library!
// Arbitrarily different to avoid conflict with master's copy.
// This ensures any bugs in my code blow up.
serverState = new State();
serverState.group("client");
serverState.group("server");
serverState.group("task", Task);

taskPool = [];

exports.start = function () {
  if (server) {
    return;
  }
  server = true;
  http.createServer(function (req, res) {
    var path = "";
    var data = [];
    req.on("data", function(body) {
      data.push(body);
    });
    switch (req.url) {
      case "/task_master":
        fs.readFile("templates/task_master.html", function (err, data) {
          res.writeHead(200, {"Content-Type": "text/html"});
          if (err) {
            throw err;
          }
          res.write(data);
          res.end();
        });
        break;
      case "/":
        req.on("end", function () {
          serverState.post(req.url, JSON.parse(data.join("")));
        });
        // TODO: Better response?
        res.writeHead(200);
        res.end("OK");
        break;
      default:
        if (req.url.indexOf("/task/") == 0) {
          var taskId = req.url.substring(6);
          taskPool.push([taskId, [req, res]]);
          processTasks();
        } else if (req.url.indexOf("/res/") == 0) {
          // URL: /res/<snapshot>/path/to/file.
          var parts = req.url.substring(5).split("/");
          // TODO: Use snapshot.
          var snapshot = parts.shift();
          path = "../../" + parts.join("/");
        } else {
          res.writeHead(404);
          res.end();
        }
    }
    if (path) {
      fs.readFile(path, function (err, data) {
        if (err) {
          throw err;
        }
        res.writeHead(200, {"Content-Type": mime.lookup(path)});
        res.end(data);
      });
    }
  }).listen(8002);
};

master.start();

var message = {};
message[uuid() + "/"] = {
  host: "localhost",
  port: "8002"
};

master.registerServer(message, function () {
  // 'registry' arg is the registered server object.
});

var NODE_HARNESS = '<script src="/res/base/' + [
      'src/always/templates/node_harness.js',
      'third_party/jasmine-node/lib/jasmine-node/jasmine-2.0.0.rc1.js'
    ].join('"><' + '/script><script src="/res/base/') +
    '"><' + '/script>';
var INCLUDE_TEMPLATE = '<script type="text/javascript">' +
    '  alias = "$SCRIPT_ALIAS";' +
    '  exports = module.exports = require(alias)' +
    '<' + '/script>\n' +
    '<script src="$SCRIPT_SRC"><' + '/script>\n' +
    '<script type="text/javascript">' +
    '  deps[alias] = module.exports;' +
    '<' + '/script>\n';

// TODO: Calculate this at runtime.
var deps = {
  "spec/always/StateTest.js": [
    "src/always/State.js"
  ],
  "spec/always/TaskTest.js": [
    "src/always/Task.js"
  ],
  "src/always/State.js": [
    "src/signal/Signal.js"
  ],
  "src/always/Task.js": [
    "src/always/State.js"
  ]
};
// TODO: Replace this with a better deps.js? Better paths? Smarter "require"?
var aliases = {
  "src/always/State.js": "always/State.js",
  "src/signal/Signal.js": "signal/Signal.js",
  "src/always/Task.js": "always/Task.js"
};

function processTasks() {
  while (taskPool.length) {
    var taskGroup = taskPool.pop();
    var taskId = taskGroup[0];
    var task = serverState.get("task").get(taskId);
    if (!task) {
      // TODO: Pretty shitty iteration. Gets stuck too easily.
      taskPool.push(taskGroup);
      console.log("Server does not know task", taskId);
      return;
    }
    var includeBase = "/res/" + task._data.snapshot + "/";
    // NB: task.data is the node with all data.
    // TODO: Better state library!
    var taskBody = NODE_HARNESS + testIncludes(includeBase, task._data.data);
    var res = taskGroup[1][1];
    fs.readFile("templates/task.html", function (err, data) {
      res.writeHead(200, {"Content-Type": "text/html"});
      if (err) {
        throw err;
      }
      var body = data.toString().replace("$TASK_ID", taskId);
      body = body.replace("$TASK_BODY", taskBody);
      res.write(body);
      res.end();
    });
  }
}

function testIncludes(base, test) {
  var result = [];
  var body;
  for (var dep in deps[test]) {
    var file = deps[test][dep];
    result.push(testIncludes(base, file));
  }
  body = INCLUDE_TEMPLATE.
      replace("$SCRIPT_ALIAS", aliases[test]).
      replace("$SCRIPT_SRC", base + test);
  result.push(body);
  return result.join("");
}
