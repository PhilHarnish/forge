angular.module("sim/Simulation.js").
    directive("travellog", function () {
      return {
        restrict: "E",
        scope: {
          player: "=",
          travelLog: "="
        },
        templateUrl: "ui/TravelLog.html"
      }
    });

angular.module("sim/ui/TravelLog.js", [
      "sim/model/Location.js"
    ]).
    controller("TravelLog", function($scope) {
      $scope.locations = $scope.travelLog.locations;
      $scope.directionText = function(location) {
        return location.distance($scope.player.data) ?
            "↑" : "×";
      };
      $scope.directionStyle = function(location) {
        var rotation = location.direction($scope.player.data).rotation;
        return {
          "-webkit-transform": "rotate(" + rotation + "rad)",
          "-moz-transform": "rotate(" + rotation + "rad)",
          "transform": "rotate(" + rotation + "rad)"
        };
      };
    }).
    factory("TravelLog", function(Location) {
      // TODO(philharnish): Restrict locations by player ID.
      function TravelLog(id) {
        this.locations = Location.query();
      }
      return TravelLog;
    });
