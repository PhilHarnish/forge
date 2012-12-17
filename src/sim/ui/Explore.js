angular.module("sim/ui/Explore.js", [
      "sim/model/Action.js",
      "sim/ui/ActionBar.js"
    ]).
    controller("Explore", Explore);

angular.module("sim/Simulation.js").
    directive("explore", function () {
      return {
        restrict: "E",
        scope: {
          player: "="
        },
        templateUrl: "ui/Explore.html"
      }
    });

function Explore($scope, Action) {
  $scope.actions = [
      new Action("fight", true),
      new Action("flight")
  ];
}
