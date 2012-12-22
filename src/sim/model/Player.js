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
        this.ui = new Ui();
      };

      Player.prototype.initialized = function() {
        return !!this.data._id;
      };

      Player.prototype.onSuccess = function() {
        // Convert `this` to services.
        this.ui.update(this.data.ui);
      };

      Player.prototype.mode = function(mode) {
        return this.ui && this.ui.mode(mode);
      };

      Player.prototype.name = function () {
        return this.data.name;
      };

      Player.prototype.stats = function() {
        return this.data.stats;
      };

      return Player;
    });
