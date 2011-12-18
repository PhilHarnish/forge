
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
      case '/task/TASK_ID':
        taskPool.push([req, res]);
        processTasks();
        break;
      case '/finished':
        console.log('Finished recorded.');
        break;
      default:
        console.log('Huh? ' + req.url);
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
    var req = task[0];
    var res = task[1];
    fs.readFile("templates/task.html", function (err, data) {
      res.writeHead(200, {'Content-Type': 'text/html'});
      if (err) {
        throw err;
      }
      res.write(data);
      res.end();
    });
  }
}

setInterval(processTasks, 100);

