
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
      snapshot: '4e21056949c926f7ac667b7149b579aa00c17b8e'
    };
    // TODO: Read tasks from request body.
    var task = new Task(uuid(), {
      client: clientId,
      snapshot: uuid(), // TODO: Temporary cache busting.
      type: 'jasmine-node',
      data: 'spec/always/TaskTest.js'
    });
    // TODO: This is a little hacky. Need new API more like:
    // state.toString('client.UUID', 'task.UUID');
    message.task[task.id] = task._data;
    task = new Task(uuid(), {
      client: clientId,
      snapshot: uuid(), // TODO: Temporary cache busting.
      type: 'jasmine-node',
      data: 'spec/always/StateTest.js'
    });
    message.task[task.id] = task._data;

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
        if (key == 'server') {
          var server;
          for (var uuid in data.server) {
            // TODO: Pick the best available server(s).
            server = data.server[uuid];
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
          var serverReq = http.request(serverOptions, function (serverRes) {
            // Don't care?
          });
          serverReq.end(JSON.stringify(message));
        } else if (key == 'task') {
          for (task in data.task) {
            daemonData[task] = data.task[task];
          }
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
        res.end(JSON.stringify(daemonData));
      });
    });
    daemonReq.end(JSON.stringify(message));
  }).listen(8000);
};

exports.test = function (test) {
  var options = {
    host: 'localhost',
    port: 8000,
    path: '/task',
    method: 'POST'
  };
  var data = [];
  var req = http.request(options, function (res) {
    res.on('data', function (chunk) {
      data.push(chunk);
    });
    res.on('end', function (chunk) {
      var results = JSON.parse(data.join(""));
      var failed = false;
      for (var task in results) {
        for (var result in results[task].results) {
          if (results[task].results[result].result != 'passed') {
            console.log('\n\n\n', task, '\n',
                results[task].results[result].messages.join('\n\n'));
            failed = true;
          }
        }
      }
      console.log();
      console.log(failed ? 'FAILED' : 'PASSED')
    });
  });
  req.write("test=" + test);
  req.end();
};

