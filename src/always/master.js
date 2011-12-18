
var fs = require('fs'),
    http = require('http'),
    querystring = require('querystring'),

    Task = require('./Task.js'),
    uuid = require('../../third_party/node-uuid/uuid.js');

var serverPool = [];
var taskMasterPool = [];
var taskPool = [];
var taskWorkerPool = [];

state = {
  server: {},
  task: {}
};
master = false;

exports.start = function () {
  if (master) {
    return;
  }
  master = true;
  http.createServer(function (req, res) {
    if (req.method == 'GET') {
      switch (req.url) {
        case '/task_master':
          taskMasterPool.push([req, res]);
          processTasks();
          break;
        case '/task':
          taskWorkerPool.push([req, res]);
          processTasks();
          break;
        default:
          res.writeHead(404);
          res.end();
      }
    } else {
      switch (req.url) {
        case '/server':
          var data = [];
          req.on('data', function(body) {
            data.push(body);
          });
          req.on('end', function() {
            // Registers a new server.
            var body = data.join('');
            var serverId = uuid();
            var input = JSON.parse(body);
            state.server[serverId] = input;
            console.log("Master stored server:", serverId, ":", input);
            res.write('{"server":{"' + serverId + '":' +
                JSON.stringify(state.server[serverId]));
            res.write('}}');
            res.end();
            serverPool.push([serverId, state.server[serverId]]);
          });
          break;
        case '/task':
          // Registers a new task.
          var task = new Task(uuid(), {
            status: Task.CREATED
          });
          state.task[task.id] = task;
          console.log('Master stored task:', task.id, ':', task.toState());
          res.write('[' + JSON.stringify(task.toState()));
          taskPool.push([task, req, res]);
          processTasks();
          var timeout;
          var completeHandler = function () {
            clearTimeout(timeout);
            if (!task.isComplete()) {
              task.set('status', Task.TIMEOUT);
            }
            res.write(',');
            res.write(JSON.stringify(task.toState()));
            res.write(']');
            res.end();
          };
          timeout = setTimeout(completeHandler, 5000);
          // TODO: subscribe to 'change'.
          task.on(Task.COMPLETE, completeHandler);
          break;
        default:
          if (req.url.indexOf('/task/') != 0) {
            res.writeHead(404);
            res.end();
            return;
          }
          var postTaskId = req.url.substring(6);
          // Registers an update for a task.
          var taskData = [];
          req.on('data', function(body) {
            taskData.push(body);
          });
          req.on('end', function() {
            var params = querystring.parse(taskData.join(''));
            for (var key in params) {
              state.task[postTaskId].set(key, params[key]);
            }
            var dest = 'http://localhost:8001/task';
            res.writeHead(302, {'Location': dest});
            res.end();
          });
          break;
      }
    }
  }).listen(8001);
};

exports.registerServer = function (server, callback) {
  var options = {
    host: 'localhost',
    port: 8001,
    path: '/server',
    method: 'POST',
    headers: {
      'Content-Type': 'application/jsonrequest'
    }
  };
  var req = http.request(options, function (res) {
    var data = [];
    res.on('data', function (chunk) {
      data.push(chunk);
    });
    res.on('end', function () {
      callback(JSON.parse(data.join('')));
    });
  });
  req.write(JSON.stringify(server));
  req.end();
};

var lastMessage = "";
function processTasks() {
  var nextMessage = ["Master processing", taskPool.length, "tasks with",
      taskWorkerPool.length, "workers and",
      serverPool.length, "servers."].join(' ');
  if (nextMessage != lastMessage) {
    lastMessage = nextMessage;
    console.log(lastMessage);
  }
  while (taskMasterPool.length && serverPool.length) {
    var taskMaster = taskMasterPool.pop();
    var taskMasterRes = taskMaster[1];
    var taskMasterDest = "http://" + serverPool[0][1].address + "/task_master";
    taskMasterRes.writeHead(302, {'Location': taskMasterDest});
    taskMasterRes.end();
  }
  while (taskPool.length && taskWorkerPool.length && serverPool.length) {
    // Pair tasks up with servers.
    var taskSet = taskPool.pop();
    var task = taskSet[0];
    var taskReq = taskSet[1];
    var taskRes = taskSet[2];
    var serverId = serverPool[0][0];
    var server = serverPool[0][1];
    taskRes.write(',');
    taskRes.write('{"server":{"' + serverId + '":' +
        JSON.stringify(server) + '}}');
    // Redirect a worker to a server.
    var worker = taskWorkerPool.pop();
    var workerRes = worker[1];
    var dest = "http://" + server.address + "/task/" + task.id;
    workerRes.writeHead(302, {'Location': dest});
    workerRes.end();
  }
}

setInterval(processTasks, 100);
