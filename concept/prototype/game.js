angular.module('game', []).
    factory('Game', function() {
      var Game = function () {
        this.start = new Date();
      };

      Game.prototype.tick = function($scope, mode) {
        var delta = new Date() - this.start;
        var future = new Date(this.start.valueOf() + delta * 24);
        future.setSeconds(0);
        $scope.time = future.toLocaleTimeString();
        if (!$scope.player.initialized()) {
          return;
        }
        var action = $scope.player.ui.mode[mode];
        this[mode]($scope, action);
        var stats = $scope.player.stats;
        if (stats.hunger > 0) {
          stats.hunger -= .05;
        }
        if (stats.health < 100) {
          stats.health += .01;
        }
      };

      Game.prototype.explore = function($scope) {
        var stats = $scope.player.stats;
        if (stats.energy > 0) {
          stats.energy -= .02;
        }
      };

      Game.prototype.rest = function($scope, action) {
        var stats = $scope.player.stats;
        var energyDelta = action == "sleep" ? 1 : .01;
        if (stats.energy < 100) {
          stats.energy += energyDelta;
        }
      };

      return Game;
    });
