from typing import Tuple

from ipywidgets import widgets

from puzzle.puzzlepedia import meta_problem, problem_widget, puzzle


def PuzzleWidget(src: puzzle.Puzzle):
  """Factory for IPython widgets, pretending to be real widget."""
  widget_children = []
  for problem in src.meta_problems():
    widget_children.append(problem_widget.ProblemWidget(problem))
  accordion = widgets.Accordion(children=widget_children)
  for i, problem in enumerate(src.meta_problems()):
    accordion.set_title(i, _get_title(problem))

  def _on_solution_change(change: Tuple[str, meta_problem.MetaProblem]) -> None:
    address, prob = change
    index = int(address.split('.').pop())
    accordion.set_title(index, _get_title(prob))

  src.subscribe(_on_solution_change)
  return accordion


def _get_title(problem: meta_problem.MetaProblem) -> str:
  active_problem = problem.active
  title = active_problem.name or str(active_problem)
  solution = problem.solution
  if solution:
    title = '%s (%s)' % (solution.upper(), title)
  return title
