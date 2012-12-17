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
          player: "="
        },
        templateUrl: "ui/Explore.html"
      }
    });

function Explore($scope, Mode) {
  this.scope = $scope;
  // TODO(philharnish): This method of extension is pretty weak.
  angular.extend(this, Mode.prototype);
  $scope.actions = this.parseActionList(Explore.ACTION_LIST);
}

Explore.ACTION_LIST = [
  "fight",
  "flight"
];

Explore.prototype = {
  fightActive: function (active) {
    if (active !== undefined && this.fightEnabled()) {
      this.scope.player.ui.modes.explore.activity = "fight";
      return true;
    }
    return this.scope.player.initialized() &&
        this.scope.player.ui.modes.explore.activity == "fight";
  },
  fightEnabled: function () {
    return this.scope.player.initialized() &&
        this.scope.player.inventory.has("weapon");
  },
  flightActive: function (active) {
    if (active !== undefined) {
      this.scope.player.ui.modes.explore.activity = "flight";
      return true;
    }
    return this.scope.player.initialized() &&
        this.scope.player.ui.modes.explore.activity == "flight";
  }
};
