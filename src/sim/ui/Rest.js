angular.module("sim/ui/Rest.js", [
      "sim/model/Action.js",
      "sim/ui/ActionBar.js"
    ]).
    controller("Rest", Rest);

angular.module("sim/Simulation.js").
    directive("rest", function () {
      return {
        restrict: "E",
        scope: {
          player: "="
        },
        templateUrl: "ui/Rest.html"
      }
    });

function Rest($scope, Action) {
  $scope.actions = [
      new Action("fortify"),
      new Action("study"),
      new Action("sleep")
  ];
}
