/* Navigation tabs. */
var fxHandlers = {
  "tab": {
    "click": function (e) {
      var tab = $(this);
      var parent = tab.parent();
      if (parent.hasClass("active")) {
        return;
      }
      // Find <a href="#target"> element with #target id.
      var target = $(tab.attr("href"));
      if (target.length == 1) {
        // Toggle parent tab active state.
        parent.addClass("active");
        parent.siblings().removeClass("active");
        // Find sibling tab-panes.
        target.addClass("active");
        target.siblings(".tab-pane").removeClass("active");
      }
    }
  }
};


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
  var classes = $(event.target).attr("class").split(" ");
  for (var i = 0; i < classes.length; i++) {
    var match = classes[i].split("fx-");
    if (match.length == 2 && !match[0] && match[1] in fxHandlers) {
      var fx = fxHandlers[match[1]];
      if (event.type in fx) {
        fx[event.type].call(event.target, event);
      }
    }
  }
}

registerFx(fxHandlers);
