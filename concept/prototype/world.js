var WORLD_SIZE = 4;
var REGION_SIZE = 128;
var ROOM_SIZE = 16;
var CACHE = false;

$(function () {
  $("#restart-button").click(restart);
});

var canvas;
var stage;
function restart () {
  canvas = $("#dropzone")[0];
  stage = new createjs.Stage(canvas);
  $("#dropzone").attr({
    width: WORLD_SIZE * REGION_SIZE,
    height: WORLD_SIZE * REGION_SIZE
  });
  var x, y;

  for (y = 0; y < WORLD_SIZE; y++) {
    for (x = 0; x < WORLD_SIZE; x++) {
      stage.addChild(makeRegion([x, y]));
    }
  }
  var scale = REGION_SIZE / ROOM_SIZE;
  for (y = 0; y < WORLD_SIZE * scale; y++) {
    for (x = 0; x < WORLD_SIZE * scale; x++) {
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
  if (!CACHE || !(metadata.id in ROOM_CACHE)) {
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

function makeRegion(position) {
  var room = new createjs.Shape(getRegionGraphics(position));
  room.x = position[0] * REGION_SIZE;
  room.y = position[1] * REGION_SIZE;
  return room;
}

var REGION_CACHE = [];
function getRegionGraphics(position) {
  var metadata = regionMetadata(position);
  var top = regionMetadata(sumPoints(position, [0, -1]));
  var left = regionMetadata(sumPoints(position, [-1, 0]));
  var id = metadata.id | (top.id << 2) | (left.id << 4);
  if (!CACHE || !(id in REGION_CACHE)) {
    REGION_CACHE[id] = new createjs.Graphics();
    var graphics = REGION_CACHE[id];
    graphics.
        //beginFill(
        //    createjs.Graphics.getRGB(metadata.color, .25)).
        //rect(0, 0, REGION_SIZE, REGION_SIZE).
        //endFill().
        //beginFill("#fff").
        drawCircle(
            REGION_SIZE / 2,
            (metadata.vertical * 2 + 1) * REGION_SIZE / 4,
            4).
        drawCircle(
            (metadata.horizontal * 2 + 1) * REGION_SIZE / 4,
            REGION_SIZE / 2,
            4).
        endFill().
        setStrokeStyle(3).
        beginStroke("#000").
        moveTo(0, 0);
    if (!top.vertical || metadata.vertical) {
      graphics.lineTo(REGION_SIZE, 0);
    }
    graphics.moveTo(0, 0);
    if (!left.horizontal || metadata.horizontal) {
      graphics.lineTo(0, REGION_SIZE);
    }
    console.log("Inserting", id, metadata);
  }
  return REGION_CACHE[id];
}
