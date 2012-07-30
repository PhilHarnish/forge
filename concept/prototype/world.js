var WORLD_SIZE = 10;
var ROOM_SIZE = 32;

$(function () {
  $("#restart-button").click(restart);
  restart();
});

var canvas;
var stage;
function restart () {
  canvas = $("#dropzone")[0];
  stage = new createjs.Stage(canvas);
  $("#dropzone").attr({
    width: WORLD_SIZE * ROOM_SIZE * 2,
    height: WORLD_SIZE * ROOM_SIZE * 2
  });
  for (var y = 0; y < WORLD_SIZE; y++) {
    for (var x = 0; x < WORLD_SIZE; x++) {
      stage.addChild(makeRoom([x, y]));
    }
  }
  stage.update();
}

function makeRoom(position) {
  var room = new createjs.Shape(getRoomGraphics(position));
  room.x = position[0] * ROOM_SIZE;
  room.y = position[1] * ROOM_SIZE;
  return room;
}

var ROOM_CACHE = [];
function getRoomGraphics(position) {
  var metadata = roomMetadata(position);
  if (!(metadata.id in ROOM_CACHE)) {
    ROOM_CACHE[metadata.id] = new createjs.Graphics();
    var graphics = ROOM_CACHE[metadata.id];
    graphics.
        beginFill("#" + metadata.color.toString(16)).
        //rect(0, 0, ROOM_SIZE, ROOM_SIZE).
        endFill().
        beginStroke("#000").
        moveTo(0, 0);
    if (!metadata.top) {
      graphics.lineTo(ROOM_SIZE, 0);
    } else if (!metadata.topWide) {
      graphics.lineTo(ROOM_SIZE / 4, 0).
          moveTo(ROOM_SIZE * (3 / 4), 0).
          lineTo(ROOM_SIZE, 0);
    }
    graphics.moveTo(0, 0);
    if (!metadata.left) {
      graphics.lineTo(0, ROOM_SIZE);
    } else if (!metadata.leftWide) {
      graphics.lineTo(0, ROOM_SIZE / 4).
          moveTo(0, ROOM_SIZE * (3 / 4)).
          lineTo(0, ROOM_SIZE);
    }
    console.log("Inserting", metadata.id, metadata);
  }
  return ROOM_CACHE[metadata.id];
}

function getIdenifier(position) {
  return "r" + position[0] + "x" + position[1];
}
