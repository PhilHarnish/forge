angular.module("sim/Simulation.js").
    directive("inventory", function () {
      return {
        restrict: "E",
        scope: {
          inventory: "="
        },
        templateUrl: "ui/Inventory.html"
      }
    });

angular.module("sim/ui/Inventory.js", [
      "sim/model/Item.js"
    ]).
    controller("Inventory", function($scope) {
      $scope.items = $scope.inventory.items;
    }).
    factory("Inventory", function(Item) {
      // TODO(philharnish): Restrict inventory by player ID.
      function Inventory(id) {
        this.items = Item.query();
      }
      Inventory.prototype.has = function (property) {
        for (var i = 0; i < this.items.length; i++) {
          var item = this.items[i];
          if (property in item.properties) {
            return true;
          }
        }
        return false;
      };
      return Inventory;
    });
