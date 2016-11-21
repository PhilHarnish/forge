// See: https://en.wikipedia.org/wiki/Heap's_algorithm

class Permute {
  /**
   * Given an array of values, produce results in lexical order.
   * @param {Array<*>} list Input to permute.
   */
  constructor(list) {
    this.original_ = Array.from(list);
    this.list = this.original_;  // Copied in reset().
    this.index = 0;
    this.state = [];
    this.permutePosition = 0;
    this.permutations = 0;
    this.size = 0;  // Calculated in reset().
    this.reset();
  }

  reset() {
    this.list = Array.from(this.original_);
    this.index = 0;
    this.permutePosition = 0;
    this.permutations = 1;  // First permutation is immediately available.
    this.size = 1;
    for (let i = 0; i < this.list.length; i++) {
      this.size *= i + 1;
      this.state[i] = 0;
    }
  }

  hasNext() {
    return this.index < this.list.length;
  }

  next()  {
    // 0123, <advance>, 0132, <advance>, 0213, <advance>, 0231, <advance>, ...
    if (this.index >= this.list.length) {
      throw new RangeError('Input list exhausted');
    }
    const result = this.list[this.index];
    this.index++;
    return result;
  }

  canAdvance() {
    return this.permutations < this.size;
  }

  advance() {
    this.index = 0;
    while (this.permutePosition < this.list.length) {
      if (this.state[this.permutePosition] < this.permutePosition) {
        if (this.permutePosition % 2 == 0) {
          // Swap 0 and i.
          [this.list[0], this.list[this.permutePosition]] = [
              this.list[this.permutePosition], this.list[0]
          ];
        } else {
          // Swap state[i] and i.
          [
              this.list[this.state[this.permutePosition]],
              this.list[this.permutePosition]
          ] = [
              this.list[this.permutePosition],
              this.list[this.state[this.permutePosition]]
          ];
        }
        this.state[this.permutePosition]++;
        this.permutePosition = 0;
        // Swap performed.
        this.permutations++;
        return;
      } else {
        this.state[this.permutePosition] = 0;
        this.permutePosition += 1;
      }
    }
    throw new RangeError('Permute list exhausted');
  }
}

module.exports = Permute;
