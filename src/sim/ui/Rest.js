angular.module("sim/ui/Rest.js", [
      "sim/model/Action.js",
      "sim/ui/ActionBar.js"
    ]).
    factory("Rest", function() {
      return Rest;
    });

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

// TODO(philharnish): Wrap object to avoid window pollution.
function Rest($scope, Action) {
  $scope.actions = [
      new Action("fortify", true),
      new Action("study"),
      new Action("sleep")
  ];
}
