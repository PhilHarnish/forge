
var fs = require('fs'),
    http = require('http'),
    querystring = require('querystring');



var serverPool = [];
var taskMasterPool = [];
var taskPool = [];
var taskWorkerPool = [];

state = {};
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
            var id = '0D4DEE04-EE57-F74B-0C70B82A1F76E149';
            console.log("Data posted to master/server:", body);
            var input = JSON.parse(body);
            state[id] = input;
            console.log("Master Stored:", id, ":", input);
            res.write('{"server":{"' + id + '":' + JSON.stringify(state[id]));
            res.write('}}');
            res.end();
            serverPool.push(state[id]);
          });
          break;
        case '/task':
          // Registers a new task.
          res.write('[{"server":{"550e8400-e29b-41d4-a716-446655440000":{');
          res.write('"address":"localhost:8002"}');
          res.write('}}');
          taskPool.push([req, res]);
          processTasks();
          setTimeout(function () {
            if (state['TASK_ID']) {
              res.write(',');
              res.write(JSON.stringify(state['TASK_ID']));
            }
            res.write(',');
            res.write('"timeout"');
            res.write(']');
            res.end();
          }, 5000);
          break;
        case '/task/TASK_ID':
          // Registers an update for a task.
          var taskData = [];
          req.on('data', function(body) {
            taskData.push(body);
          });
          req.on('end', function() {
            console.log('body for /task/TASK_ID:', taskData.join(''));
            var params = querystring.parse(taskData.join(''));
            state['TASK_ID'] = {};
            for (var key in params) {
              state['TASK_ID'][key] = params[key];
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
    var taskMasterDest = "http://" + serverPool[0].address + "/task_master";
    taskMasterRes.writeHead(302, {'Location': taskMasterDest});
    taskMasterRes.end();
  }
  while (taskPool.length && taskWorkerPool.length && serverPool.length) {
    // Pair tasks up with servers.
    var task = taskPool.pop();
    // Redirect a worker to a server.
    var server = serverPool[0];
    var worker = taskWorkerPool.pop();
    var workerRes = worker[1];
    var dest = "http://" + server.address + "/task/TASK_ID";
    workerRes.writeHead(302, {'Location': dest});
    workerRes.end();
  }
}

setInterval(processTasks, 100);
