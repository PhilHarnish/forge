angular.module('sim/model/Player.js', [
      'sim/model/Inventory.js',
      'sim/model/Item.js',
      'sim/model/MongolabEndpoint.js',
      'sim/model/Ui.js'
    ]).
    factory('Player', function(Inventory, Item, MongolabEndpoint, Ui) {
      var PlayerEndpoint = MongolabEndpoint('sim-players/:id');
      var Player = function (id) {
        this.data = PlayerEndpoint.get({"id": id},
            angular.bind(this, this.onSuccess));
        this.inventory = new Inventory(Item.query());
      };

      Player.prototype.initialized = function() {
        return !!this.data._id;
      };

      Player.prototype.onSuccess = function() {
        // Convert `this` to services.
        this.ui = new Ui(this.data.ui);
      };

      Player.prototype.mode = function(mode) {
        if (!this.initialized()) {
          return false;
        } else if (mode !== undefined) {
          this.ui.setMode(mode);
        }
        return this.ui.mode;
      };

      Player.prototype.name = function () {
        return this.data.name;
      };

      Player.prototype.stats = function() {
        return this.data.stats;
      };

      return Player;
    });
