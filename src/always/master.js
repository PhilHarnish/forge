
var fs = require("fs"),
    http = require("http"),
    querystring = require("querystring"),

    State = require("always/State.js"),
    Task = require("always/Task.js"),
    uuid = require("node-uuid/uuid.js");

var serverPool = [];
var taskMasterPool = [];
var taskPool = [];
var taskWorkerPool = [];

state = new State();
state.group("client");
state.group("server");
state.group("task", Task);
master = false;

exports.start = function () {
  if (master) {
    return;
  }
  master = true;
  var current = {};
  state.get("task").onAdded.add(function (task) {
    addTask(task, current.req, current.res);
  });
  state.get("server").onAdded.add(function (server) {
    console.log("Master stored server:",
        server.toString());
    serverPool.push(server);
  });
  http.createServer(function (req, res) {
    var task,
        taskId;
    if (req.method == "GET") {
      switch (req.url) {
        case "/task_master":
          taskMasterPool.push([req, res]);
          processTasks();
          break;
        case "/task":
          taskWorkerPool.push([req, res]);
          processTasks();
          break;
        default:
          res.writeHead(404);
          res.end();
      }
    } else {
      var data = [];
      req.on("data", function(body) {
        data.push(body);
      });
      switch (req.url) {
        case "/":
          req.on("end", function () {
            current.req = req;
            current.res = res;
            var body = data.join("");
            var updates = JSON.parse(body);
            state.post(req.url, updates);
          });
          break;
        case "/server":
          req.on("end", function() {
            // Registers a new server.
            var body = data.join("");
            console.log("New server data:", body);
            var updates = JSON.parse(body);
            state.post(req.url, updates);
            res.end(body);
          });
          break;
        default:
          if (req.url.indexOf("/task/") != 0) {
            res.writeHead(404);
            res.end();
            break;
          }
          taskId = req.url.substring(6);
          // Registers an update for a task.
          req.on("end", function() {
            var params = querystring.parse(data.join(""));
            // TODO: Hacky?
            var status;
            if ("status" in params) {
              status = params.status;
              delete params.status;
            }
            if ("results" in params) {
              params.results = JSON.parse(params.results);
            }
            for (var key in params) {
              state.get("task").get(taskId).set(key, params[key]);
            }
            if (status) {
              state.get("task").get(taskId).set("status", status);
            }
            var dest = "http://localhost:8001/task";
            res.writeHead(302, {"Location": dest});
            res.end();
          });
          break;
      }
    }
  }).listen(8001);
};

function addTask(task, req, res) {
  console.log("Master stored task:", task.toString());
  res.write("[" + task.toString());
  taskPool.push([task, req, res]);
  processTasks();
  var timeout;
  // TODO: Writing to res is hacky.
  res.pendingCount = res.pendingCount || 0;
  res.pendingCount++;
  var completeHandler = function () {
    clearTimeout(timeout);
    res.pendingCount--;
    if (!task.isComplete()) {
      task.set("status", Task.TIMEOUT);
    }
    res.write(",");
    res.write(task.toString());
    // TODO: This assumes no one else has added tests.
    if (!res.pendingCount) {
      res.write("]");
      res.end();
    }
  };
  timeout = setTimeout(completeHandler, 5000);
  // TODO: subscribe to "change".
  task.onComplete.add(completeHandler);
}

exports.registerServer = function (server, callback) {
  var options = {
    host: "localhost",
    port: 8001,
    path: "/server",
    method: "POST",
    headers: {
      "Content-Type": "application/jsonrequest"
    }
  };
  var req = http.request(options, function (res) {
    var data = [];
    res.on("data", function (chunk) {
      data.push(chunk);
    });
    res.on("end", function () {
      callback(JSON.parse(data.join("")));
    });
  });
  req.write(JSON.stringify(server));
  req.end();
};

var lastMessage = "";
function processTasks() {
  var nextMessage = ["Master processing", taskPool.length, "tasks with",
      taskWorkerPool.length, "workers and",
      serverPool.length, "servers."].join(" ");
  if (nextMessage != lastMessage) {
    lastMessage = nextMessage;
    console.log(lastMessage);
  }
  while (taskMasterPool.length && serverPool.length) {
    var taskMaster = taskMasterPool.pop();
    var taskMasterRes = taskMaster[1];
    var taskMasterDest = "http://" + serverPool[0].get("host") + ":" +
        serverPool[0].get("port") + "/task_master";
    taskMasterRes.writeHead(302, {"Location": taskMasterDest});
    taskMasterRes.end();
  }
  while (taskPool.length && taskWorkerPool.length && serverPool.length) {
    // Pair tasks up with servers.
    var taskSet = taskPool.pop();
    var task = taskSet[0];
    var taskRes = taskSet[2];
    var server = serverPool[0];
    taskRes.write(",");
    taskRes.write(server.toString());
    // Redirect a worker to a server.
    var worker = taskWorkerPool.pop();
    var workerRes = worker[1];
    var dest = "http://" + serverPool[0].get("host") + ":" +
        serverPool[0].get("port") + "/task/" + task.id;
    workerRes.writeHead(302, {"Location": dest});
    workerRes.end();
  }
}
