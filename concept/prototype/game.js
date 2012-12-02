var DEBUG_TIME_MULTIPLE = 4;

angular.module('game', []).
    factory('Game', function() {
      var SECOND = 1000;
      var MINUTE = 60 * SECOND;
      var HOUR = 60 * MINUTE;
      var DAY = 24 * HOUR; // Milliseconds in a day.
      var DAY_MULTIPLIER = 24 * DEBUG_TIME_MULTIPLE; // 1 hour = 24 hours.
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

        var stats = $scope.player.stats;
        increment(stats, "hunger", HUNGER_RATE, elapsed);
        increment(stats, "energy", FATIGUE_RATE, elapsed);
        if (stats.hunger <= 0) {
          increment(stats, "health", PERISH_RATE, elapsed);
        } else if (stats.health < 100) {
          increment(stats, "health", RECOVER_RATE, elapsed);
        }
      };

      Game.prototype.explore = function($scope, action, elapsed) {
        var stats = $scope.player.stats;
      };

      Game.prototype.rest = function($scope, action, elapsed) {
        var stats = $scope.player.stats;
        var items = $scope.items;
        if (action == "sleep") {
          increment(stats, "energy", SLEEP_RATE, elapsed);
        } else {
          if (stats.hunger < 10) {
            var eaten = 0;
            console.log("Trying to eat from:", items);
            do {
              var itemIndex = findItemIndexWithProperty(items, "food");
              if (itemIndex >= 0) {
                consume(items, itemIndex, stats);
              } else {
                break;
              }
            } while (stats.hunger < 80 && eaten++ < 3);
          }
        }
      };

      return Game;

      function increment(stats, stat, rate, elapsed) {
        stats[stat] =
            Math.max(0, Math.min(stats[stat] + rate * elapsed, 100));
      }

      function findItemIndexWithProperty(items, property) {
        for (var i = 0; i < items.length; i++) {
          var item = items[i];
          if (!item.consumed && item.properties[property]) {
            return i;
          }
        }
        return -1;
      }

      function consume(items, index, stats) {
        var item = items[index];
        item.consumed = true;
        item.owned = false;
        for (var property in item.properties) {
          switch (property) {
            case "food":
              increment(stats, "hunger", MEAL, 1);
              break;
          }
        }
      }
    });
