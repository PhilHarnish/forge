var spec = require("../../test"),
    fixtures = require("spec/revolver/fixtures"),
    genfiles = require("spec/revolver/fixtures/genfiles.js"),
    revolver = require("src/revolver/revolver.js");

var cwd = process.cwd(),
    deps,
    app;

// TODO: Find a way to test this in isolation.
// Unloading everything appears to wreak havoc.
xdescribe("hermetic requirements", function () {
  it("should empty the cache", function () {
    expect(revolver.getCacheList().length).toBeGreaterThan(0);
    revolver.unloadAll();
    expect(revolver.getCacheList()).toEqual([]);
  });
});

xdescribe("revolver", function () {
  beforeEach(function () {
    deps = fixtures.getDeps();
    require.paths.push(genfiles.setup(deps));
    global.importOrder = [];
    global.executeOrder = [];
  });

  afterEach(function () {
    require.paths.pop();
    genfiles.cleanup();
    revolver.unloadAll();
    if (revolver.getCacheList().length > 0) {
      require("sys").exit(1);
    }
    delete global.importOrder;
    delete global.executeOrder;
  });

  it("should require the application successfully", function () {
    app = require("views/SignIn.js");
    expect(app.name).toEqual("views/SignIn.js");
    expect(global.importOrder).toBeDefined();
    expect(global.importOrder.length).toBeGreaterThan(0);
    expect(global.importOrder).toEqual(
        fixtures.getImportOrder("views/SignIn.js"));
    expect(global.executeOrder).toEqual(
        fixtures.getExecuteOrder("views/SignIn.js"));
  });

  it("should reload everything", function () {
    app = require("views/SignIn.js");
    var expected = fixtures.getImportOrder("views/SignIn.js");
    expect(global.importOrder).toEqual(expected);
    revolver.unload(fixtures.getImportOrder("views/SignIn.js"));
    // And again...
    app = require("views/SignIn.js");
    expect(global.importOrder).toEqual(expected.concat(expected));
  });

  it("should reload some, reuse others", function () {
    app = require("views/SignIn.js");
    expect(global.importOrder).toEqual(
        fixtures.getImportOrder("views/SignIn.js"));
    // Simulate changing Button.js.
    var affected = fixtures.getAffected("ui/Button.js");
    var oldImportLength = global.importOrder.length;
    revolver.unload(affected);
    app = require("views/SignIn.js");
    var reloaded = global.importOrder.slice(oldImportLength);
    // NB: Not everything in "affected" is reloaded, eg tests.
    for (var i = 0; i < reloaded.length; i++) {
      expect(affected).toContain(reloaded[i]);
    }
  });
});
