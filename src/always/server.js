
var fs = require('fs'),
    http = require('http'),
    master = require('./master.js');

server = false;

// Returns files which contain task masters and tasks


taskPool = [];

exports.start = function () {
  if (server) {
    return;
  }
  server = true;
  http.createServer(function (req, res) {
    console.log(req.url);
    var path = '';
    switch (req.url) {
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
  address: 'localhost:8002'
}, function(registry) {
  console.log("Registered with: " + registry);
});

function processTasks() {
  while (taskPool.length) {
    var task = taskPool.pop();
    var taskId = task[0];
    var req = task[1][0];
    var res = task[1][1];
    fs.readFile("templates/task.html", function (err, data) {
      res.writeHead(200, {'Content-Type': 'text/html'});
      if (err) {
        throw err;
      }
      res.write(data.toString().replace('TASK_ID', taskId));
      res.end();
    });
  }
}

setInterval(processTasks, 100);

