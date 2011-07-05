// Main file for cloud_demo.html

var MARGIN = 75;
var TILE_SIZE = 32;
var camera = {
  x: Math.round(Number.MAX_VALUE / 2),
  y: Math.round(Number.MAX_VALUE / 2),
  z: Math.round(Number.MAX_VALUE / 2),
  rotation: Math.PI / 4,
  angle: Math.PI / 4
};
var viewport;

var stage;
$(function () {
  stage = new Raphael("stage", "100%", "100%");
  redraw(stage);
});

function redraw(stage) {
  stage.clear();
  drawGrid(stage);
  drawViewport(stage);
}

function drawGrid(stage) {
  var v = getViewport();
  var virtualX = 0;
  var virtualY = 0;
  for (var y = v.y - TILE_SIZE / 2; y - v.y < v.height; y += TILE_SIZE / 2) {
    var start = virtualY % 2 ? v.x - TILE_SIZE / 2 : v.x;
    virtualY++;
    for (var x = start; x - v.x < v.width; x += TILE_SIZE) {
      getTile(stage, x, y);
    }
  }
}

function drawViewport(stage) {
  var v = getViewport();
  stage.rect(v.x, v.y, v.width, v.height).attr("stroke", "white");
}

function getViewport() {
  if (!viewport) {
    var w = $(window).width();
    var h = $(window).height();
    viewport = {
      x: MARGIN,
      y: MARGIN,
      width: w - MARGIN * 2,
      height: h - MARGIN * 2
    };
  }
  return viewport;
}
$(window).resize(function () {
  viewport = null;
  redraw(stage);
});

function getTilePath(camera) {
  path = [
    (-TILE_SIZE / 2) + ",0",
    "0," + (-TILE_SIZE / 2),
    (TILE_SIZE / 2) + ",0",
    "0," + (TILE_SIZE / 2),
    (-TILE_SIZE / 2) + ",0"
  ];
  return "M" + path.join("L");
}

function getTile(stage, x, y) {
  return stage.path(getTilePath(camera)).attr({
    stroke: "gray",
    fill: "salmon"
  }).translate(x, y);
}
