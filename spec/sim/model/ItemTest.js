var spec = require("../../../test"),
    Item = require("angular.js/build/angular-resource.js");
    Item = require("sim/model/Item.js");

describe("Item", function() {
  beforeEach(angular.mock.module('sim/db/Item.js'));

  it("should create items.", function(Item) {
    expect(Item).toBeTruthy();
  });
});
