
angular.module('simulation', ['location', 'item', 'player', 'game']).
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
  directive('items', function () {
    return {
      restrict: 'E',
      templateUrl: 'partials/items.html'
    }
  }).
  directive('locations', function () {
    return {
      restrict: 'E',
      templateUrl: 'partials/locations.html'
    }
  });

function SimController($scope, $location, $timeout, Player, Game, Item) {
  $scope.items = Item.query();
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
  $scope.game = new Game();
  var tick = function () {
    $scope.game.tick($scope, $location.path().slice(1));
    $timeout(tick, 500);
  };
  tick();
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
}

function ItemsController($scope, Item) {
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
