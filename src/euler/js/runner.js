var _ = require("../../../third_party/underscore/underscore.js")._;

//var problems = [1, 2, 3, 4];
var problems = [4];

_(problems).each(function (i) {
  console.log();
  console.log("Running problem " + i);
  var problem = require("./problem_" + i + ".js");
  console.log.apply(console, problem.preamble);
  for (var approach in problem.solutions) {
    var start = (new Date).getTime();
    var solution = problem.solutions[approach]();
    console.log(approach + ":", solution, "(in",
        ((new Date).getTime() - start) + "ms)");
  }
});
