var ARROW = {
  LEFT: 37,
  UP: 38,
  RIGHT: 39,
  DOWN: 40
};
var ROOM_TILES = 9;
var TILE_SIZE = 50;
var MARGINS = 2;
var ROOM_SIZE = ROOM_TILES * (TILE_SIZE + MARGINS);
var ROOM_CACHE = {};

var position = [0, 0];

$(function () {
  $("#viewport").css({
    width: ROOM_SIZE,
    height: ROOM_SIZE
  });
  $("#restart-button").click(restart);
  restart();
});

$(document).keydown(function (e) {
  switch (e.which) {
    case ARROW.LEFT:
      position = move(position, [-1, 0]);
      break;
    case ARROW.RIGHT:
      position = move(position, [1, 0]);
      break;
    case ARROW.UP:
      position = move(position, [0, -1]);
      break;
    case ARROW.DOWN:
      position = move(position, [0, 1]);
      break;
    default:
      return true;
  }
  return false;
});

function restart() {
  position = [0, 0];
  ROOM_CACHE = {};
  $("#dropzone").empty().append(makeRoom(position));
}

function makeRoom(position) {
  var id = getIdenifier(position);
  if (!(id in ROOM_CACHE)) {
    var result = [];
    for (var ry = 0; ry < ROOM_TILES; ry++) {
      result.push("<tr>");
      for (var rx = 0; rx < ROOM_TILES; rx++) {
        result.push(
            "<td class='" + tileStatus(position, [rx, ry]) + "'></td>")
      }
      result.push("</tr>");
    }
    ROOM_CACHE[id] = $("<table class='room'" +
        "id='" + id + "' style='top: 0; left: 0'>" +
        result.join("") + "</table>");
  }
  return ROOM_CACHE[id];
}

function move(position, delta) {
  // First, make and position the adjacent room.
  var newPosition = sumPoints(position, delta);
  var adjacent = makeRoom(newPosition);
  adjacent.css(getOffset(delta));
  $("#dropzone").append(adjacent);
  adjacent.stop().animate(getOffset([0, 0]));

  // Next, position the existing room.
  var room = getIdenifier(position, true);
  $(room).stop().animate(getOffset(multiplyPoints([-1, -1], delta)),
    {
      complete: function () {
        $(this).remove();
      }
    }
  );

  return newPosition;
}

function getIdenifier(position, hash) {
  return (hash ? "#r" : "r") +
      position[0] + "x" + position[1];
}

function getOffset(delta) {
  var dx = delta[0];
  var dy = delta[1];
  return {
    top: dy * ROOM_SIZE,
    left: dx * ROOM_SIZE
  };
}

function multiplyPoints(a, b) {
  return [a[0] * b[0], a[1] * b[1]]
}
