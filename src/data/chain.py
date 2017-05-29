class Chain(list):
  def __init__(self, data):
    if isinstance(data, int):
      size = data
      data = range(0, size)
    else:
      size = len(data)
    super(Chain, self).__init__(data)
    self._head = 0
    self._next_links = list(range(1, size))
    if size:
      self._active = [True] * size
      self._next_links.append(None)
      self._back_links = [None]
      self._back_links.extend(range(0, size - 1))
    else:
      self._active = []
      self._back_links = []
    self._tail = size - 1
    self._size = size
    self._pop_stack = []

  def __iter__(self):
    cursor = self._head
    while cursor is not None:
      yield cursor
      cursor = self._next_links[cursor]

  def __len__(self):
    return self._size

  def items(self):
    cursor = self._head
    while cursor is not None:
      yield cursor, self[cursor]
      cursor = self._next_links[cursor]

  def pop(self, index=None):
    if index is None:
      index = self._tail
    elif index < 0:
      raise NotImplementedError('Negative indexes are not implemented.')
    elif not self._active[index]:
      raise IndexError('pop from empty list')
    self._active[index] = False
    self._size -= 1
    self._pop_stack.append(index)
    forward = self._next_links[index]
    backward = self._back_links[index]
    if backward is None:  # Head truncation.
      self._head = forward
      if forward is not None:
        self._back_links[forward] = None  # Backwards from "forward" is None.
    elif forward is not None:
      self._back_links[forward] = backward
    if forward is None:  # Tail truncation.
      self._tail = backward
      if backward is not None:
        self._next_links[backward] = None  # Forwards from "backward" is None.
    elif backward is not None:
      self._next_links[backward] = forward

  def restore(self, i):
    index = self._pop_stack[-1]
    if index != i:
      raise IndexError('restore sync error: expected %s got %s' % (index, i))
    self._active[index] = True
    self._size += 1
    self._pop_stack.pop()
    backward = self._back_links[index]
    forward = self._next_links[index]
    if backward is None:  # Restoring first node.
      self._head = index
    else:
      self._next_links[backward] = index
    if forward is None:  # Restoring last node.
      self._tail = index
    else:
      self._back_links[forward] = index
