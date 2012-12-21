angular.module("sim/model/Inventory.js", []).
    factory("Inventory", function() {
      function Inventory(items) {
        this.items = items;
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
