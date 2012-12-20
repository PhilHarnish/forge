angular.module("sim/ui/Explore.js", [
      "sim/model/Mode.js",
      "sim/ui/ActionBar.js"
    ]).
    controller("Explore", Explore);

angular.module("sim/Simulation.js").
    directive("explore", function () {
      return {
        restrict: "E",
        scope: {
          mode: "=",
          player: "="
        },
        templateUrl: "ui/Explore.html"
      }
    });

function Explore($scope) {
  this.scope = $scope;
  // TODO(philharnish): Watching for changes is not ideal.
  $scope.$watch("mode", function (mode) {
    if (mode) {
      $scope.actions = mode.parseActionList(Explore.ACTION_LIST);
    }
  });
}

Explore.ACTION_LIST = [
  {
    name: "fight",
    enabled: false
  },
  {
    name: "flight"
  }
];
