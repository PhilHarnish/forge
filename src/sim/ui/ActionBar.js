angular.module("sim/ui/ActionBar.js", []).
    controller("ActionBar", ActionBar);

angular.module("sim/Simulation.js").
    directive("actionbar", function () {
      return {
        restrict: "E",
        scope: {
          actions: "=",
          mode: "=",
          player: "="
        },
        templateUrl: "ui/ActionBar.html"
      }
    });

function ActionBar($scope) {
  $scope.classes = function (action) {
    return {
      active: action.active(),
      disabled: !action.enabled()
    }
  };
}
