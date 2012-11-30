
angular.module('simulation', ['location', 'player']).
  config(function($routeProvider) {
    $routeProvider.
      when('/explore', {
          controller: ExploreController,
          templateUrl: 'partials/explore.html'
      }).
      when('/rest', {
          controller: RestController,
          templateUrl: 'partials/rest.html'
      }).
      otherwise({redirectTo:'/explore'});
  }).
  directive('actionbar', function () {
      return {
        restrict: 'E',
        templateUrl: 'partials/actionbar.html'
      }
  }).
  directive('locations', function () {
    return {
      restrict: 'E',
      templateUrl: 'partials/locations.html'
    }
  });

function SimController($scope, $location, $timeout, Player) {
  $scope.player = Player.get({id: "50b6f69be4b0dbae32c8ece1"}, function (p) {
    if (p.name) {
      // Initialized.
      return;
    }
    p.name = "philharnish";
    p.stats = {
      health: 20,
      hunger: 40,
      energy: 60
    };
    p.ui = {
      mode: {
        explore: "flight",
        rest: "fortify"
      }
    };

    p.$save();
  });
  $scope.modeIs = function(mode) {
    return $location.path() == '/' + mode;
  };
  var start = new Date();
  var update = function() {
    gameLoop($scope, $location, $timeout, start, update);
  };
  update();
}

function gameLoop($scope, $location, $timeout, start, update) {
  $timeout(update, 500);
  var delta = new Date() - start;
  var future = new Date(start.valueOf() + delta * 24);
  future.setSeconds(0);
  $scope.time = future.toLocaleTimeString();
  if (!$scope.player.initialized()) {
    return;
  }
  switch ($location.path()) {
    case '/explore':
      explore($scope);
      break;
    case '/rest':
      rest($scope);
      break;
  }
  var stats = $scope.player.stats;
  if (stats.hunger > 0) {
    stats.hunger -= .05;
  }
  if (stats.health < 100) {
    stats.health += .01;
  }
}

function explore($scope) {
  var stats = $scope.player.stats;
  if (stats.energy > 0) {
    stats.energy -= .02;
  }
}

function rest($scope) {
  var stats = $scope.player.stats;
  var action = $scope.player.ui.mode.rest;
  var energyDelta = action == "sleep" ? 1 : .01;
  if (stats.energy < 100) {
    stats.energy += energyDelta;
  }
}

function MeterController($scope) {
  $scope.meters = ["health", "hunger", "energy"];
}

function ExploreController($scope) {
  $scope.actions = [
    {
      name: "fight",
      disabled: true,
      active: actionGetterSetter($scope, "explore")
    },
    {
      name: "flight",
      active: actionGetterSetter($scope, "explore")
    }
  ];
}

function LocationsController($scope, Location) {
  $scope.locations = Location.query();
}

function RestController($scope) {
  $scope.actions = [
    {
      name: "fortify",
      active: actionGetterSetter($scope, "rest")
    },
    {
      name: "study",
      active: actionGetterSetter($scope, "rest")
    },
    {
      name: "sleep",
      active: actionGetterSetter($scope, "rest")
    }
  ];
  $scope.items = [
    {
      name: "bat",
      owned: true,
      weight: 2
    },
    {
      name: "canned food",
      owned: true,
      weight: 3
    }
  ];
}

function actionGetterSetter($scope, mode) {
  if (!$scope.hasOwnProperty("$actionGetterSetter")) {
    $scope.$actionGetterSetter =
        function (value) {
          if (value === undefined) {
            return $scope.player.ui &&
                $scope.player.ui.mode[mode] == this.name;
          } else if (!this.disabled && value) {
            $scope.action = this;
            $scope.player.ui.mode[mode] = this.name;
            $scope.player.update();
          }
          return value;
        };
  }
  return $scope.$actionGetterSetter;
}
