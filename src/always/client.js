
var http = require('http'),

    Task = require('always/Task.js'),
    uuid = require('node-uuid/uuid.js');

client = false;

exports.start = function () {
  if (client) {
    return;
  }
  client = true;
  http.createServer(function (req, res) {
    var message = {
      client: {
      },
      task: {
      }
    };
    var clientId = uuid();
    message.client[clientId] = {
      src: 'git://url',
      rev: '4e21056949c926f7ac667b7149b579aa00c17b8e'
    };
    // TODO: Read tasks from request body.
    var task = new Task(uuid(), {
      client: clientId,
      type: 'jasmine-node',
      data: 'always/TaskTest.js'
    });
    // TODO: This is a little hacky. Need new API more like:
    // state.toString('client.UUID', 'task.UUID');
    message.task[task.id] = task.data;

    // Simulate initiating a test run.
    var options = {
      host: 'localhost',
      port: 8001,
      path: '/',
      method: 'POST',
      headers: {
        'Content-Type': 'application/jsonrequest'
      }
    };

    var daemonData = {};
    var dataHandler = function(data) {
      // Ignore arrays and strings.
      if (data.length) {
        return;
      }
      for (var key in data) {
        daemonData[key] = data[key];
        if (key == 'server') {
          console.log('Need to notify:', data[key]);
          var server;
          for (var uuid in data[key]) {
            // TODO: Pick the best available server(s).
            server = data[key][uuid];
          }
          var serverOptions = {
            host: server.host,
            port: server.port,
            path: '/',
            method: 'POST',
            headers: {
              'Content-Type': 'application/jsonrequest'
            }
          };
          console.log('Sending server:', serverOptions.host,
              serverOptions.port, serverOptions.path);
          console.log(JSON.stringify(message));
          var serverReq = http.request(serverOptions, function (serverRes) {
            // Don't care?
          });
          serverReq.write(JSON.stringify(message));
          serverReq.end();
        }
      }
    };
    // Simulate initiating a test run.
    options.port = 8001;
    var daemonReq = http.request(options, function (daemonRes) {
      var acc = "";
      var payloadStart = 1;
      var payloadEnd = payloadStart;
      var inString = false;
      var depth = 0;
      var data = [];
      daemonRes.on('data', function (chunk) {
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
              break;
            case '"':
              if (!depth) {
                payloadStart = payloadEnd;
              }
              if (inString) {
                depth--;
              } else {
                depth++;
              }
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
        res.write(JSON.stringify(daemonData));
        res.end();
      });
    });
    daemonReq.end(JSON.stringify(message));
  }).listen(8000);
};

exports.test = function (test) {
  var options = {
    host: 'localhost',
    port: 8000,
    path: '/test',
    method: 'POST'
  };
  var data = [];
  var req = http.request(options, function (res) {
    res.on('data', function (chunk) {
      data.push(chunk);
    });
    res.on('end', function (chunk) {
      console.log('Test ended:', data.join(''));
    });
  });
  req.write("test=" + test);
  req.end();
};

