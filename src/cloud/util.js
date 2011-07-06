// Misc. utilities used by main.js

var cameraCache = {};
function setCamera(newCamera) {
  var key = newCamera.rotation + "x" + newCamera.tilt;
  if (!cameraCache[key]) {
    cameraCache[key] = {
      _id: key,
      x: Math.round(newCamera.x),
      y: Math.round(newCamera.y),
      z: Math.round(newCamera.z),
      rotation: newCamera.rotation,
      _rotationCos: Math.cos(newCamera.rotation * Math.PI),
      _rotationSin: Math.sin(newCamera.rotation * Math.PI),
      tilt: newCamera.tilt,
      _tiltCos: Math.cos(Math.atan(Math.sin(newCamera.tilt * Math.PI))),
      _tiltSin: Math.sin(Math.atan(Math.sin(newCamera.tilt * Math.PI)))
    };
    console.log(cameraCache[key]);
  }
  return cameraCache[key];
}

var tileCache = {};
function getTilePath(camera) {
  if (!tileCache[camera._id]) {
    var path = _([[-1, -1], [1, -1], [1, 1], [-1, 1], [-1, -1]]).map(toPath);
    console.log(path);
    var extra = "M0,0L" + transformX(camera, 0, -TILE_SIZE / 2, 0) + "," +
        transformY(camera, 0, -TILE_SIZE / 2, 0);

    tileCache[camera._id] = "M" + path.join("L") + extra;
  }
  return tileCache[camera._id];
}

function toPath(point) {
  return Math.round(transformX(camera,
          point[0] * TILE_SIZE / 2,
          point[1] * TILE_SIZE / 2,
          (point[2] || 0) * TILE_SIZE / 2)) + "," +
      Math.round(transformY(camera,
          point[0] * TILE_SIZE / 2,
          point[1] * TILE_SIZE / 2,
          (point[2] || 0) * TILE_SIZE / 2));
 }

function transformX(camera, x, y, z) {
  return x * camera._rotationCos - y * camera._rotationSin;
}

function transformY(camera, x, y, z) {
  return x * camera._tiltCos * camera._rotationSin +
      y * camera._tiltCos * camera._rotationCos -
      z * camera._tiltSin;
}
