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
          player: "="
        },
        templateUrl: "ui/Rest.html"
      }
    });

function Rest($scope, Mode) {
  this.scope = $scope;
  // TODO(philharnish): This method of extension is pretty weak.
  angular.extend(this, Mode.prototype);
  $scope.actions = this.parseActionList(Rest.ACTION_LIST);
}

Rest.ACTION_LIST = [
  "fortify",
  "sleep"
];

Rest.prototype = {
  fortifyActive: function (active) {
    if (active !== undefined && this.fightEnabled()) {
      this.scope.player.ui.modes.rest.activity = "fortify";
      return true;
    }
    return this.scope.player.initialized() &&
        this.scope.player.ui.modes.rest.activity == "fortify";
  },
  sleepActive: function (active) {
    if (active !== undefined) {
      this.scope.player.ui.modes.rest.activity = "sleep";
      return true;
    }
    return this.scope.player.initialized() &&
        this.scope.player.ui.modes.rest.activity == "sleep";
  }
};
