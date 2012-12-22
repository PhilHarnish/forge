angular.module("sim/model/Inventory.js", [
      "sim/model/Item.js"
    ]).
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
