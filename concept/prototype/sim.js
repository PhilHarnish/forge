
angular.module('simulation', []).
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
  });

function MeterController($scope) {
  $scope.meters = [
    {
      name: "health",
      value: 20,
      css: "info"
    },
    {
      name: "hunger",
      value: 40,
      css: "success"
    },
    {
      name: "energy",
      value: 60,
      css: "warning"
    }
  ];
}

function ExploreController($scope) {
  $scope.actions = [
    {
      name: "fight",
      disabled: true,
      active: false
    },
    {
      name: "flight",
      disabled: false,
      active: true
    }
  ];
  var distance = function () {
    return this.x + this.y + this.z;
  };
  var cssRotation = function () {
    var rotation = 33 * (this.x + this.y + this.z);
    return {
      "-webkit-transform": "rotate(" + rotation + "deg)",
      "-moz-transform": "rotate(" + rotation + "deg)",
      "transform": "rotate(" + rotation + "deg)"
    };
  };
  $scope.locations = [
    {
      name: "base",
      memorable: true,
      distance: distance,
      cssRotation: cssRotation,
      x: 0,
      y: 0,
      z: 0
    },
    {
      name: "locked door",
      memorable: true,
      distance: distance,
      cssRotation: cssRotation,
      x: 0,
      y: 10,
      z: 0
    },
    {
      name: "hostile",
      memorable: false,
      distance: distance,
      cssRotation: cssRotation,
      x: 10,
      y: 10,
      z: 0
    }
  ];
}

function RestController($scope) {
  $scope.actions = [
    {
      name: "fortify",
      active: true
    },
    {
      name: "study",
      active: false
    },
    {
      name: "sleep",
      active: false
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
