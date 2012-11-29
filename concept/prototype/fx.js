var fxHandlers = {
};

function mutex (el, match) {
  el.addClass("active");
  el.siblings(match).removeClass("active");
}

/* Setup handlers on body. */
function registerFx(fxHandlers) {
  var added = {};
  var b = $("body");
  for (var fx in fxHandlers) {
    for (var type in fxHandlers[fx]) {
      if (!added[type]) {
        b.on(type, handle);
        added[type] = true;
      }
    }
  }
}

function handle(event) {
  var attr = $(event.target).attr("class");
  if (!attr) {
    return true;
  }
  var classes = attr.split(" ");
  if (classes.indexOf("disabled") >= 0) {
    return false;
  }
  for (var i = 0; i < classes.length; i++) {
    var match = classes[i].split("fx-");
    if (match.length == 2 && !match[0] && match[1] in fxHandlers) {
      var fx = fxHandlers[match[1]];
      if (event.type in fx) {
        fx[event.type].call(event.target, event);
      }
    }
  }
  return true;
}

registerFx(fxHandlers);
