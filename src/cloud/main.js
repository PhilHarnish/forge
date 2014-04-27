// Main file for cloud_demo.html

var MARGIN = 75;
var TILE_SIZE = 200;
var camera = setCamera({
  x: Math.round(Number.MAX_VALUE / 2),
  y: Math.round(Number.MAX_VALUE / 2),
  z: Math.round(Number.MAX_VALUE / 2),
  rotation: 1 / 4, // radians (without PI)
  tilt: 30 / 100 // radians (without PI)
});

var viewport;

var stage;
$(function () {
  stage = new Raphael("stage", "100%", "100%");
  redraw(stage);
  $("#rotation").change(function () {
    var c = _(camera).clone();
    c.rotation = $(this).val() / 100;
    camera = setCamera(c);
    redraw(stage);
  });
  $("#tilt").change(function () {
    var c = _(camera).clone();
    c.tilt = $(this).val() / 100;
    camera = setCamera(c);
    redraw(stage);
  });
});

function redraw(stage) {
  stage.clear();
  //drawGrid(stage);
  drawCube(stage);
  drawViewport(stage);
}

function drawCube(stage) {
  var path;
  /* */
  path = _([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 0]]).map(toPath);
  stage.path("M" + path.join("L")).attr({
    stroke: "white",
    "stroke-dasharray": "-"
  }).translate(200, 100);
  path = _([[0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1], [0, 0, 1]]).map(toPath);
  stage.path("M" + path.join("L")).attr({
    stroke: "white",
    "stroke-dasharray": "-"
  }).translate(200, 100);
  /* */
  path = _([[0, 0, 0], [1, 0, 0]]).map(toPath);
  stage.path("M" + path.join("L")).attr({
    stroke: "red"
  }).translate(200, 100);
  path = _([[0, 0, 0], [0, 1, 0]]).map(toPath);
  stage.path("M" + path.join("L")).attr({
    stroke: "green"
  }).translate(200, 100);
  path = _([[0, 0, 0], [0, 0, 1]]).map(toPath);
  stage.path("M" + path.join("L")).attr({
    stroke: "blue"
  }).translate(200, 100);
  path = _([[0, 0, 0], [1, 1, 1]]).map(toPath);
  stage.path("M" + path.join("L")).attr({
    stroke: "white"
  }).translate(200, 100);
}

function drawGrid(stage) {
  var v = getViewport();
  var virtualX = 0;
  var virtualY = 0;
  //for (var y = v.y - TILE_SIZE / 2; y - v.y < v.height; y += TILE_SIZE / 2) {
    var start = virtualY % 2 ? v.x - TILE_SIZE / 2 : v.x;
    virtualY++;
    for (var x = start; x - v.x < v.width; x += TILE_SIZE) {
      getTile(stage, x, 100);
    }
  //}
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

function getTile(stage, x, y) {
  return stage.path(getTilePath(camera)).attr({
    stroke: "gray",
    fill: "salmon"
  }).translate(x, y);
}
