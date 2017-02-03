Polymer({
  is: 'origen-seven-segment',

  properties: {
    data: {
      type: Array,
      observer: 'dataChanged_'
    },
  },

  dataChanged_: function(data) {
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    path.setAttribute('fill', '#DDD');
    let cmds = [];
    for (let col = 0; col < data.length; col++) {
      const segments = data[col];
      const x = Math.floor(col / 2);
      if (col % 2) {
        // Horizontal segments.
        const top = segments & 1;
        const middle = segments & 2;
        const bottom = segments & 4;
        if (top) {
          this.appendSegment_(cmds, x, 0, false);
        }
        if (middle) {
          this.appendSegment_(cmds, x, 1, false);
        }
        if (bottom) {
          this.appendSegment_(cmds, x, 2, false);
        }
      } else {
        // Vertical segments.
        const top = segments & 1;
        const bottom = segments & 2;
        if (top) {
          this.appendSegment_(cmds, x, 0, true);
        }
        if (bottom) {
          this.appendSegment_(cmds, x, 1, true);
        }
      }
    }
    path.setAttribute('d', cmds.join(' '));
    console.log(data);
    this.$.svg.appendChild(path);
  },

  appendSegment_(cmds, x, y, vertical) {
    const WIDTH = 8;
    const HEIGHT = 40;
    const GAP = 5;
    const SPACING = 2 * GAP + 2 * WIDTH + HEIGHT;
    const startX = x * SPACING + (vertical ? 0 : GAP + WIDTH) + WIDTH;
    const startY = y * SPACING + (vertical ? GAP + WIDTH : 0) + WIDTH;
    const dir = vertical ? 'v' : 'h';
    cmds.push(`M${startX},${startY}`);
    if (vertical) {
      cmds.push(`m0,${-WIDTH}`);  // Top.
      cmds.push(`l${-WIDTH},${WIDTH}`);  // Top left.
    } else {
      cmds.push(`m${-WIDTH},0`);  // Left.
      cmds.push(`l${WIDTH},${-WIDTH}`);  // Top left.
    }
    cmds.push(`${dir}${HEIGHT}`);  // Bottom left.
    cmds.push(`l${WIDTH},${WIDTH}`);  // Bottom.
    if (vertical) {
      cmds.push(`l${WIDTH},${-WIDTH}`);  // Bottom right.
    } else {
      cmds.push(`l${-WIDTH},${WIDTH}`);  // Bottom right.
    }
    cmds.push(`${dir}${-HEIGHT}`);  // Bottom left.
  },
});
