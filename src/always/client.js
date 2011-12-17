
var http = require('http');

var client;
exports.start = function () {
  if (client) {
    return;
  }
  client = http.createServer(function (req, res) {
    var daemonData = {};
    var dataHandler = function(data) {
      for (var key in data) {
        daemonData[key] = data[key];
      }
    };
    // Simulate initiating a test run.
    var options = {
      host: 'localhost',
      port: 8001,
      path: '/task',
      method: 'POST',
      headers: {
        'Content-Type': 'application/jsonrequest'
      }
    };
    var daemonReq = http.request(options, function (daemonRes) {
      var acc = "";
      var payloadStart = 1;
      var payloadEnd = payloadStart;
      var inString = false;
      var depth = 0;
      var data = [];
      daemonRes.on('data', function (chunk) {
        console.log('FROM DAEMON: ' + chunk);
        acc += chunk;
        while (payloadEnd < acc.length) {
          switch (acc[payloadEnd]) {
            case '{':
              if (!depth) {
                payloadStart = payloadEnd;
              }
              depth++;
              break;
            case '}':
              depth--;
            case '"':
              inString = !inString;
              break;
            case '\\':
              payloadEnd++;
          }
          payloadEnd++;
          if (!depth && payloadStart < payloadEnd) {
            var parsed = JSON.parse(acc.substring(payloadStart, payloadEnd));
            payloadStart = payloadEnd + 1;
            data.push(parsed);
            dataHandler(parsed);
          }
        }
      });
      daemonRes.on('end', function () {
        res.writeHead(200, {'Content-Type': 'text/plain'});
        res.write('Daemon response to client: ' + acc);
        res.write('JSON received: ' + JSON.stringify(data));
        res.end();
      });
    });
    daemonReq.write('[{src: "git",' +
        'rev: "4e21056949c926f7ac667b7149b579aa00c17b8e",' +
        'tests: ["templates/task.html"]}]\n');
    daemonReq.end();
  }).listen(8000);
};

exports.test = function () {
  var options = {
    host: 'localhost',
    port: 8000,
    path: '/test',
    method: 'POST'
  };
  http.request(options, function (res) {
    res.on('data', function (chunk) {
      console.log('BODY: ' + chunk);
    });
  }).end();
};

