import rx
from ipywidgets import widgets


def ProblemWidget(meta_problem):
  """Factory for IPython widgets, pretending to be real widget."""
  items = []
  options = {}
  for problem in meta_problem:
    options[problem.kind] = problem
  # Dropdown.
  dropdown = widgets.Dropdown(options=options)
  items.append(dropdown)
  dropdown_source = _observable_for_widget(dropdown)

  def _on_problem_kind_change(problem):
    _update_label_for_problem(solutions, best_solution, problem)

  dropdown_source.subscribe(_on_problem_kind_change)
  # Best solution.
  best_solution = widgets.Text()
  items.append(best_solution)
  best_solution_source = _observable_for_widget(best_solution)

  def _on_best_solution_change(solution):
    meta_problem.solution = solution

  best_solution_source.subscribe(_on_best_solution_change)
  solutions = widgets.Label('...calculating...')
  if meta_problem.peek():
    _update_label_for_problem(solutions, best_solution, meta_problem.peek())
  return widgets.VBox([widgets.HBox(items), solutions])


def _update_label_for_problem(label, best_solution, problem):
  solutions = problem.solutions()
  if solutions.peek():
    best_solution.value = solutions.peek()
  label.value = str(solutions)


def _observable_for_widget(widget):
  def subscribe(observer):
    def _on_change(change):
      observer.on_next(change['new'])

    widget.observe(_on_change, names='value')

  return rx.AnonymousObservable(subscribe)
