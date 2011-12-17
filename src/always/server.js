
var fs = require('fs'),
    http = require('http');

var server;

// Returns files which contain task masters and tasks
workerPool = [];

exports.start = function () {
  if (server) {
    return;
  }
  server = http.createServer(function (req, res) {
    console.log(req.url);
    var path = '';
    switch (req.url) {
      case '/task_master':
        path = 'templates/task_master.html';
      break;
      case '/task':
        workerPool.push(res);
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
