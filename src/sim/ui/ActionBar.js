angular.module("sim/ui/ActionBar.js", []).
    factory("ActionBar", function() {
      return ActionBar;
    });

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

// TODO(philharnish): Wrap object to avoid window pollution.
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
