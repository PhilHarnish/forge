def puzzle(source: str, hint: str = None, threshold: float = None):
  from puzzle.puzzlepedia import puzzlepedia
  return puzzlepedia.parse(source, hint=hint, threshold=threshold)
