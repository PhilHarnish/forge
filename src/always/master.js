
var fs = require('fs'),
    http = require('http'),
    querystring = require('querystring'),
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
  console.log("listening on 8001");
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
            console.log("Data posted to master/server:", body);
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
          var taskId = uuid();
          state.task[taskId] = {
            status: "created"
          };
          var message = {
            task: {}
          };
          message.task[taskId] = state.task[taskId];
          res.write('[' + JSON.stringify(message));
          taskPool.push([taskId, [req, res]]);
          processTasks();
          setTimeout(function () {
            if (state.task[taskId]) {
              res.write(',');
              res.write(JSON.stringify(message));
            }
            res.write(',');
            res.write('"timeout"');
            res.write(']');
            res.end();
          }, 5000);
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
            console.log('body for /task/TASK_ID:', taskData.join(''));
            var params = querystring.parse(taskData.join(''));
            for (var key in params) {
              state.task[postTaskId][key] = params[key];
            }
            var dest = 'http://localhost:8001/task';
            res.writeHead(302, {'Location': dest});
            res.end();
          });
          break;
      }
    }
  }).listen(8001);
  console.log('Master:', master);
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
      console.log('master/server BODY: ' + chunk);
      data.push(chunk);
    });
    res.on('end', function () {
      console.log("Attempting to parse: ", data.join(''));
      callback(JSON.parse(data.join('')));
    });
  });
  req.write(JSON.stringify(server));
  req.end();
};

function processTasks() {
  console.log("Master processing", taskPool.length, "tasks with",
      taskWorkerPool.length, "workers and",
      serverPool.length, "servers.");
  while (taskMasterPool.length && serverPool.length) {
    var taskMaster = taskMasterPool.pop();
    var taskMasterRes = taskMaster[1];
    var taskMasterDest = "http://" + serverPool[0][1].address + "/task_master";
    taskMasterRes.writeHead(302, {'Location': taskMasterDest});
    taskMasterRes.end();
  }
  while (taskPool.length && taskWorkerPool.length && serverPool.length) {
    // Pair tasks up with servers.
    var task = taskPool.pop();
    var taskId = task[0];
    var taskReq = task[1][0];
    var taskRes = task[1][1];
    var serverId = serverPool[0][0];
    var server = serverPool[0][1];
    taskRes.write(',');
    taskRes.write('{"server":{"' + serverId + '":' +
        JSON.stringify(server) + '}}');
    // Redirect a worker to a server.
    var worker = taskWorkerPool.pop();
    var workerRes = worker[1];
    var dest = "http://" + server.address + "/task/" + taskId;
    workerRes.writeHead(302, {'Location': dest});
    workerRes.end();
  }
}

setInterval(processTasks, 100);
