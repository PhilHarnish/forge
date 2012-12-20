angular.module("sim/ui/Rest.js", [
      "sim/model/Mode.js",
      "sim/ui/ActionBar.js"
    ]).
    controller("Rest", Rest);

angular.module("sim/Simulation.js").
    directive("rest", function () {
      return {
        restrict: "E",
        scope: {
          mode: "=",
          player: "="
        },
        templateUrl: "ui/Rest.html"
      }
    });

function Rest($scope) {
  this.scope = $scope;
   // TODO(philharnish): Watching for changes is not ideal.
  $scope.$watch("mode", function (mode) {
    if (mode) {
      $scope.actions = mode.parseActionList(Rest.ACTION_LIST);
    }
  });
}

Rest.ACTION_LIST = [
  {
    name: "fortify"
  },
  {
    name: "sleep"
  }
];
