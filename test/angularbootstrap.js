window.jasmine = true;
window.beforeEach = function (fn) {
  angular.mock.before = fn;
};
window.afterEach = function (fn) {
  angular.mock.after = fn;
};
