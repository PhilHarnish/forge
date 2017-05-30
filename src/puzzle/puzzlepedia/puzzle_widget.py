from ipywidgets import widgets

from puzzle.puzzlepedia import problem_widget


def PuzzleWidget(puzzle):
  """Factory for IPython widgets, pretending to be real widget."""
  widget_children = []
  for problem in puzzle._meta_problems:
    widget_children.append(problem_widget.ProblemWidget(problem))
  accordion = widgets.Accordion(children=widget_children)
  for i, problem in enumerate(puzzle._meta_problems):
    accordion.set_title(i, _get_title(problem))

  def _on_solution_change(change):
    address, problem = change
    index = int(address.split('.').pop())
    accordion.set_title(index, _get_title(problem))

  puzzle.subscribe(_on_solution_change)
  return accordion


def _get_title(problem):
  src = '\n'.join(problem.active.lines)
  solution = problem.solution
  if solution:
    src = '%s (%s)' % (solution.upper(), src)
  return src
