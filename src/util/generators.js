module.exports = {
  /**
   * @param {number} start
   * @param {number} end
   * @param {number} increment
   * @return {Array<number>} Array from [start, end).
   */
  range(start, end, increment = 1) {
    if (!increment ||
        (increment > 0 && end < start) ||
        (increment < 0 && end > start)) {
      throw new RangeError();
    }
    const result = new Array(end - start);
    for (let i = start; i < end; i += increment) {
      result[i] = i;
    }
    return result;
  },
};
