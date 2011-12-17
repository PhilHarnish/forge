
var http = require('http');

var serverMap = {};
var master;

exports.start = function () {
  if (master) {
    return;
  }
  master = http.createServer(function (req, res) {
    if (req.method == 'GET') {
      res.writeHead(302, {'Location': 'http://localhost:8001/task_master'});
      res.end();
    } else {
      switch (req.url) {
        case '/server':
          // Registers a new server.
          break;
      }
      res.write('[{"550e8400-e29b-41d4-a716-446655440000":{');
      res.write('"server":"localhost:8002"}');
      res.write('}');
      setTimeout(function () {
        res.write(']');
        res.end();
      }, 2000);
    }
  }).listen(8001);
};
