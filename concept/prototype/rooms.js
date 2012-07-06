var ARROW = {
  LEFT: 37,
  UP: 38,
  RIGHT: 39,
  DOWN: 40
};
var ROOM_TILES = 7;
var TILE_SIZE = 50;
var MARGINS = 3;
var ROOM_SIZE = ROOM_TILES * (TILE_SIZE + MARGINS);
var ROOM_CACHE = {};

var position = [0, 0];

$(function () {
  $("#restart-button").click(restart);
  restart();
});

$(document).keyup(function (e) {
  switch (e.which) {
    case ARROW.LEFT:
      console.log("LEFT");
      position = move(position, [-1, 0]);
      break;
    case ARROW.RIGHT:
      console.log("RIGHT");
      position = move(position, [1, 0]);
      break;
    case ARROW.UP:
      console.log("UP");
      position = move(position, [0, -1]);
      break;
    case ARROW.DOWN:
      console.log("DOWN");
      position = move(position, [0, 1]);
      break;
    default:
      return true;
  }
  return false;
});

function restart() {
  $("#dropzone").empty().append(makeRoom(position));
}

function makeRoom(position) {
  var id = getIdenifier(position);
  if (!(id in ROOM_CACHE)) {
    var result = [];
    for (var ry = 0; ry < ROOM_TILES; ry++) {
      result.push("<tr>");
      for (var rx = 0; rx < ROOM_TILES; rx++) {
        result.push("<td class='" + tileStatus(position, rx, ry) + "'>" +
            rx + "x" + ry + "</td>")
      }
      result.push("</tr>");
    }
    ROOM_CACHE[id] = $("<table class='room' id='" + id + "'>" +
        result.join("") + "</table>");
  }
  return ROOM_CACHE[id];
}

function tileStatus(position, rx, ry) {
  if (rx == 3 || ry == 3) {
    return "room-vacant";
  } else if (rx % (ROOM_TILES - 1) && ry % (ROOM_TILES - 1)) {
    return "room-vacant";
  }
  return "room-blocked";
}

function move(position, delta) {
  // First, make and position the adjacent room.
  var newPosition = sumPoints(position, delta);
  var adjacent = makeRoom(newPosition);
  adjacent.css(getOffset(delta));
  $("#dropzone").append(adjacent);
  adjacent.animate(getOffset([0, 0]));

  // Next, position the existing room.
  var room = getIdenifier(position, true);
  $(room).animate(getOffset(multiplyPoints([-1, -1], delta)),
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

function sumPoints(a, b) {
  return [a[0] + b[0], a[1] + b[1]];
}

function multiplyPoints(a, b) {
  return [a[0] * b[0], a[1] * b[1]]
}
