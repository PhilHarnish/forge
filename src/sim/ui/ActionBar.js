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
  $scope.active = function (action) {
    if ($scope.player.initialized()) {
      return $scope.mode.activity == action.name;
    }
    return false;
  };
  $scope.activate = function (action) {
    if (!action.disabled) {
      $scope.mode.activity = action.name;
    }
  };
}
