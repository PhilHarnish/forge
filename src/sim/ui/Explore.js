angular.module("sim/ui/Explore.js", [
      "sim/model/Action.js",
      "sim/ui/ActionBar.js"
    ]).
    factory("Explore", function() {
      return Explore;
    });

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

// TODO(philharnish): Wrap object to avoid window pollution.
function Explore($scope, Action) {
  $scope.actions = [
      new Action("fight", false, true),
      new Action("flight", true)
  ];
}
