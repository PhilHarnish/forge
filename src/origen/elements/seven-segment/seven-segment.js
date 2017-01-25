Polymer({
  is: 'seven-segment',

  properties: {
    data: {
      type: Array,
      observer: 'dataChanged_'
    },
    computedPath_: {
      type: String
    }
  },

  dataChanged_: function(data) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('height', '100');
    svg.setAttribute('width', '100');
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('d', 'M10 10 H 90 V 90 H 10 L 10 10');
    path.setAttribute('fill', '#DDD');
    console.log(data);
    svg.appendChild(path);
    this.$.dz.appendChild(svg);
  },
});
