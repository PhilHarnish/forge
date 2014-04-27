

function findAncestor(t, varargs) {
  var find = [];
  for (var i = 1; i < arguments.length; i++) {
    find.push(arguments[i]);
  }
  var best = null;
  findAncestor_(t);
  return best;

  function findAncestor_(n) {
    if (!n || best) {
      return [];
    }
    var i;
    var foundAll = true;
    var found = [];
    var left = findAncestor_(n.left);
    var right = findAncestor_(n.right);
    for (i = 0; i < find.length; i++) {
      if ((n.value == find[i]) || left[i] || right[i]) {
        found[i] = true;
      }
      foundAll = found[i] && foundAll;
    }
    if (foundAll && !best) {
      best = n;
    }
    return found;
  }
}
