var tempFoodItems = 5;

angular.module('game', []).
    factory('Game', function() {
      var SECOND = 1000;
      var MINUTE = 60 * SECOND;
      var HOUR = 60 * MINUTE;
      var DAY = 24 * HOUR; // Milliseconds in a day.
      var DAY_MULTIPLIER = 24; // 1 hour = 24 hours.
      var SLEEP_NEEDED = 5 * HOUR;
      var MAX_WAKING_HOURS = 20 * HOUR; // Max time between sleeps.
      var MEAL = 25; // Meal value.
      var MAX_FAST = 15 * HOUR; // Max time between meals.
      var RECOVERY = 7 * DAY;
      var DEHYDRATION = 3 * DAY;

      var SLEEP_RATE = 100 / SLEEP_NEEDED;
      var FATIGUE_RATE = -100 / MAX_WAKING_HOURS;
      var HUNGER_RATE = -100 / MAX_FAST;
      var RECOVER_RATE = 100 / RECOVERY;
      var PERISH_RATE = -100 / DEHYDRATION;

      var Game = function () {
        this.start = new Date();
        this.lastTick = false;
      };

      Game.prototype.tick = function($scope, mode) {
        var now = new Date();
        var delta = now - this.start;
        var future = new Date(this.start.valueOf() + delta * DAY_MULTIPLIER);
        future.setSeconds(0);
        $scope.time = future.toLocaleTimeString();
        if (!$scope.player.initialized()) {
          return;
        } else if (!this.lastTick) {
          // TODO(philharnish): Pull last tick from $scope.player.
          this.lastTick = now;
        }
        var elapsed = (now - this.lastTick) * DAY_MULTIPLIER;
        // Action is explore or rest.
        var action = $scope.player.ui.mode[mode];
        this[mode]($scope, action, elapsed);

        this.increment($scope, "hunger", HUNGER_RATE, elapsed);
        var stats = $scope.player.stats;
        if (stats.hunger < 10 && tempFoodItems-- > 0) {
          // TODO(philharnish): Implement food items.
          this.increment($scope, "hunger", MEAL, 1);
        }
        if (stats.hunger <= 0) {
          this.increment($scope, "health", PERISH_RATE, elapsed);
        } else if (stats.health < 100) {
          this.increment($scope, "health", RECOVER_RATE, elapsed);
        }
      };

      Game.prototype.explore = function($scope, action, elapsed) {
        this.increment($scope, "energy", FATIGUE_RATE, elapsed);
      };

      Game.prototype.rest = function($scope, action, elapsed) {
        if (action == "sleep") {
          this.increment($scope, "energy", SLEEP_RATE, elapsed);
        }
      };

      Game.prototype.increment = function ($scope, stat, rate, elapsed) {
        var stats = $scope.player.stats;
        stats[stat] =
            Math.max(0, Math.min(stats[stat] + rate * elapsed, 100));
      };

      return Game;
    });
