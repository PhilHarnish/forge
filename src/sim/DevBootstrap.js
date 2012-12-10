(function () {
  /*
   * Stop automatic bootstrapping.
   */
  // Find the element with @ng-app attribute.
  var head = document.getElementsByTagName("head")[0];
  var appElements = document.querySelectorAll('[ng-app]');
  var appElement;
  var appModule;
  if (appElements.length) {
    // Store the result.
    appElement = appElements[0];
    appModule = appElement.getAttribute('ng-app');
    // And disable auto-bootstrapping.
    appElement.removeAttribute('ng-app');
    loadScript(appModule);
  }

  /*
   * Dynamic module loading.
   */
  var module = angular.module;
  var loading = {};
  var loadingCount = 0;
  var timeout;
  // Override angular.module to detect needed dependencies and when those
  // dependencies have loaded.
  angular.module = function(name, requires, configFn) {
    var loadedModule = module(name, requires, configFn);
    if (loading[name]) {
      loading[name] = false;
      loadingCount--;
    }
    if (requires) {
      for (var i = 0; i < requires.length; i++) {
        // Only attempt to load modules which appear to be files.
        var dep = requires[i];
        if (!(dep in loading) && dep.slice(-3) == ".js") {
          loading[requires[i]] = true;
          loadingCount++;
          clearTimeout(timeout);
          timeout = setTimeout(loadTimeout, 1000);
          loadScript(requires[i]);
        }
      }
    }
    if (!loadingCount && appElement && appModule) {
      clearTimeout(timeout);
      // Need to wait for call to angular.module() to return so that the
      // subsequent call to "factory" can also complete.
      setTimeout(function () {
        angular.bootstrap(appElement, [appModule]);
      }, 0);
    }
    return loadedModule;
  };

  // TODO(philharnish): Calculating commonPrefix is possible if needed.
  function loadScript(src) {
    var script = document.createElement("script");
    script.src = src.replace(/^sim\//, "");
    head.appendChild(script);
  }

  function loadTimeout() {
    console.log("Failed to load", loadingCount, "resources");
    console.log(loading);
  }
})();
