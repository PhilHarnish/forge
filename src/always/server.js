
var fs = require('fs'),
    http = require('http'),
    master = require('always/master.js'),

    Task = require('always/Task.js');

server = false;

// Returns files which contain task masters and tasks

// TODO: centralized state library!
// Arbitrarily different to avoid conflict with master's copy.
// This ensures any bugs in my code blow up.
serverState = {
  client: {},
  server: {},
  task: {}
};

taskPool = [];

exports.start = function () {
  if (server) {
    return;
  }
  server = true;
  http.createServer(function (req, res) {
    var path = '';
    var data = [];
    req.on('data', function(body) {
      data.push(body);
    });
    switch (req.url) {
      case '/':
        // TODO: FIXME. Duplicated code from master.js.
        req.on('end', function () {
          var body = data.join('');
          var updates = JSON.parse(body);
          console.log('Server parsed:', updates);
          // TODO: Manual merging is lame.
          var uuid;
          for (uuid in updates.client) {
            serverState.client[uuid] = updates.client[uuid];
            console.log("Server stored client:", uuid, ":",
                updates.client[uuid]);
          }
          for (uuid in updates.task) {
            if (uuid in serverState.task) {
              task = serverState.task[uuid];
              for (var key in updates.task[uuid]) {
                task.set(key, updates.task[uuid][key]);
              }
            } else {
              task = new Task(uuid, updates.task[uuid]);
              serverState.task[uuid] = task;
              console.log('Server stored task:', task.toState());
            }
          }
        });
        // TODO: Better response?
        res.writeHead(200);
        res.end('OK');
        break;
      case '/task_master':
        fs.readFile('templates/task_master.html', function (err, data) {
          res.writeHead(200, {'Content-Type': 'text/html'});
          if (err) {
            throw err;
          }
          res.write(data);
          res.end();
        });
        break;
      default:
        if (req.url.indexOf('/task/') == 0) {
          var taskId = req.url.substring(6);
          taskPool.push([taskId, [req, res]]);
          processTasks();
        } else {
          res.writeHead(404);
          res.end();
        }
    }
    if (path) {
      fs.readFile(path, function (err, data) {
        res.writeHead(200, {'Content-Type': 'text/html'});
        if (err) {
          throw err;
        }
        res.write(data);
        res.end();
      });
    }
  }).listen(8002);
};

master.start();

master.registerServer({
  host: 'localhost',
  port: '8002'
}, function() {
  // 'registry' arg is the registered server object.
});



var TEST_HEADER = '<script type="text/javascript">';
var TEST_FOOTER = '</script>';



function processTasks() {
  while (taskPool.length) {
    var taskGroup = taskPool.pop();
    var taskId = taskGroup[0];
    if (!(taskId in serverState.task)) {
      // TODO: Pretty shitty iteration. Gets stuck too easily.
      taskPool.push(taskGroup);
      console.log('Server does not know', taskId);
      return;
    }
    var task = serverState.task[taskId];
    // NB: task.data is the node with all data.
    // TODO: Better state library!
    var path = '../../spec/' + task.data.data;
    // TODO: simultaneous data and template file reads!
    var taskBody = TEST_HEADER + fs.readFileSync(path) + TEST_FOOTER;
    var res = taskGroup[1][1];
    fs.readFile('templates/task.html', function (err, data) {
      res.writeHead(200, {'Content-Type': 'text/html'});
      if (err) {
        throw err;
      }
      var body = data.toString().replace('$TASK_ID', taskId);
      body = body.replace('$TASK_BODY', taskBody);
      res.write(body);
      res.end();
    });
  }
}

setInterval(processTasks, 100);
