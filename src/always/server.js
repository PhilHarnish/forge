
var fs = require('fs'),
    http = require('http'),
    master = require('always/master.js'),

    mime = require('node-mime/mime.js'),
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
              console.log('Server stored task:', task.toString());
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
        } else if (req.url.indexOf('/res/') == 0) {
          // URL: /res/<snapshot>/path/to/file.
          var parts = req.url.substring(5).split('/');
          // TODO: Use snapshot.
          var snapshot = parts.shift();
          path = '../../' + parts.join('/');
        } else {
          res.writeHead(404);
          res.end();
        }
    }
    if (path) {
      fs.readFile(path, function (err, data) {
        if (err) {
          throw err;
        }
        res.writeHead(200, {'Content-Type': mime.lookup(path)});
        res.end(data);
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

var NODE_HARNESS = '<script src="/res/base/' + [
      'src/always/templates/node_harness.js',
      'third_party/jasmine-node/lib/jasmine-node/jasmine-2.0.0.rc1.js'
    ].join('"><' + '/script><script src="/res/base/') +
    '"><' + '/script>';
var INCLUDE_TEMPLATE = '<script type="text/javascript">' +
    '  alias = "$SCRIPT_ALIAS";' +
    '  exports = module.exports = require(alias)' +
    '<' + '/script>\n' +
    '<script src="$SCRIPT_SRC"><' + '/script>\n' +
    '<script type="text/javascript">' +
    '  deps[alias] = module.exports;' +
    '<' + '/script>\n';

// TODO: Calculate this at runtime.
var deps = {
  'spec/always/StateTest.js': [
    'third_party/node/lib/util.js', // TODO: Temp.
    'third_party/node/lib/assert.js', // TODO: Temp.
    'third_party/should/lib/should.js', // TODO: Temp.
    'src/always/State.js'
  ],
  'spec/always/TaskTest.js': [
    'third_party/node/lib/util.js', // TODO: Temp.
    'third_party/node/lib/assert.js', // TODO: Temp.
    'third_party/should/lib/should.js', // TODO: Temp.
    'src/always/Task.js'
  ],
  'src/always/State.js': [
    'third_party/node/lib/events.js'
  ],
  'src/always/Task.js': [
    'third_party/node/lib/events.js',
    'src/always/State.js'
  ]
};
// TODO: Replace this with a better deps.js? Better paths? Smarter "require"?
var aliases = {
  'src/always/State.js': 'always/State.js',
  'src/always/Task.js': 'always/Task.js',
  'third_party/node/lib/assert.js': 'assert',
  'third_party/node/lib/events.js': 'events',
  'third_party/node/lib/util.js': 'util',
  'third_party/should/lib/should.js': 'should'
};

function processTasks() {
  while (taskPool.length) {
    var taskGroup = taskPool.pop();
    var taskId = taskGroup[0];
    if (!(taskId in serverState.task)) {
      // TODO: Pretty shitty iteration. Gets stuck too easily.
      taskPool.push(taskGroup);
      console.log('Server does not know task', taskId);
      return;
    }
    var task = serverState.task[taskId];
    var includeBase = '/res/' + task._data.snapshot + '/';
    // NB: task.data is the node with all data.
    // TODO: Better state library!
    var taskBody = NODE_HARNESS + testIncludes(includeBase, task._data.data);
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

function testIncludes(base, test) {
  var result = [];
  var body;
  for (var dep in deps[test]) {
    var file = deps[test][dep];
    result.push(testIncludes(base, file));
  }
  body = INCLUDE_TEMPLATE.
      replace('$SCRIPT_ALIAS', aliases[test]).
      replace('$SCRIPT_SRC', base + test);
  result.push(body);
  return result.join('');
}

setInterval(processTasks, 100);
