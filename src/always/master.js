
var fs = require('fs'),
    http = require('http'),
    querystring = require('querystring'),

    State = require('always/State.js'),
    Task = require('always/Task.js'),
    uuid = require('node-uuid/uuid.js');

var serverPool = [];
var taskMasterPool = [];
var taskPool = [];
var taskWorkerPool = [];
/*
state = {
  client: {},
  server: {},
  task: {}
};
*/
state = new State();
state.client = {};
state.server = {};
state.add("task", Task);
master = false;

exports.start = function () {
  if (master) {
    return;
  }
  master = true;
  http.createServer(function (req, res) {
    var task,
        taskId;
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
      var data = [];
      req.on('data', function(body) {
        data.push(body);
      });
      switch (req.url) {
        case '/':
          req.on('end', function () {
            var body = data.join('');
            var updates = JSON.parse(body);
            // TODO: Manual merging is lame.
            var uuid;
            for (uuid in updates.client) {
              state.client[uuid] = updates.client[uuid];
              console.log('Master stored client:', uuid, ':',
                  updates.client[uuid]);
            }
            for (uuid in updates.task) {
              task = state.get('task').get(uuid);
              if (task) {
                for (var key in updates.task[uuid]) {
                  task.set(key, updates.task[uuid][key]);
                }
              } else {
                addTask(uuid, updates.task[uuid], req, res);
              }
            }
          });
          break;
        case '/server':
          req.on('end', function() {
            // Registers a new server.
            var body = data.join('');
            var serverId = uuid();
            var input = JSON.parse(body);
            state.server[serverId] = input;
            console.log('Master stored server:', serverId, ':', input);
            res.write('{"server":{"' + serverId + '":' +
                JSON.stringify(state.server[serverId]));
            res.write('}}');
            res.end();
            serverPool.push([serverId, state.server[serverId]]);
          });
          break;
        case '/task':
          // Registers a new task.
          addTask(uuid(), {}, req, res);
          break;
        default:
          if (req.url.indexOf('/task/') != 0) {
            res.writeHead(404);
            res.end();
            break;
          }
          taskId = req.url.substring(6);
          // Registers an update for a task.
          req.on('end', function() {
            var params = querystring.parse(data.join(''));
            // TODO: Hacky?
            var status;
            if ('status' in params) {
              status = params.status;
              delete params.status;
            }
            if ('results' in params) {
              params.results = JSON.parse(params.results);
            }
            for (var key in params) {
              state.get("task").get(taskId).set(key, params[key]);
            }
            if (status) {
              state.get("task").get(taskId).set('status', status);
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

function addTask(id, data, req, res) {
  var task = state.get("task").get(id);
  if (!task) {
    task = state.get("task").add(id, Task, data);
  }
  console.log('Master stored task:', task.toString());
  res.write('[' + task.toString());
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
      task.set('status', Task.TIMEOUT);
    }
    res.write(',');
    res.write(task.toString());
    // TODO: This assumes no one else has added tests.
    if (!res.pendingCount) {
      res.write(']');
      res.end();
    }
  };
  timeout = setTimeout(completeHandler, 5000);
  // TODO: subscribe to 'change'.
  task.on(Task.COMPLETE, completeHandler);
}

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

var lastMessage = '';
function processTasks() {
  var nextMessage = ['Master processing', taskPool.length, 'tasks with',
      taskWorkerPool.length, 'workers and',
      serverPool.length, 'servers.'].join(' ');
  if (nextMessage != lastMessage) {
    lastMessage = nextMessage;
    console.log(lastMessage);
  }
  while (taskMasterPool.length && serverPool.length) {
    var taskMaster = taskMasterPool.pop();
    var taskMasterRes = taskMaster[1];
    var taskMasterDest = 'http://' + serverPool[0][1].host + ':' +
        serverPool[0][1].port + '/task_master';
    taskMasterRes.writeHead(302, {'Location': taskMasterDest});
    taskMasterRes.end();
  }
  while (taskPool.length && taskWorkerPool.length && serverPool.length) {
    // Pair tasks up with servers.
    var taskSet = taskPool.pop();
    var task = taskSet[0];
    var taskRes = taskSet[2];
    var serverId = serverPool[0][0];
    var server = serverPool[0][1];
    taskRes.write(',');
    taskRes.write('{"server":{"' + serverId + '":' +
        JSON.stringify(server) + '}}');
    // Redirect a worker to a server.
    var worker = taskWorkerPool.pop();
    var workerRes = worker[1];
    var dest = 'http://' + serverPool[0][1].host + ':' +
        serverPool[0][1].port + '/task/' + task.id;
    workerRes.writeHead(302, {'Location': dest});
    workerRes.end();
  }
}

setInterval(processTasks, 100);
