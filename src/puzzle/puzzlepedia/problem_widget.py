import rx
from ipywidgets import widgets

from puzzle.puzzlepedia import table_widget


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
    _update_solutions_for_problem(solutions_table, best_solution, problem)

  dropdown_source.subscribe(_on_problem_kind_change)
  # Best solution.
  best_solution = widgets.Text()
  items.append(best_solution)
  best_solution_source = _observable_for_widget(best_solution)

  def _on_best_solution_change(solution):
    meta_problem.solution = solution

  best_solution_source.subscribe(_on_best_solution_change)
  solutions_table = table_widget.TableWidget()
  if meta_problem.peek():
    _update_solutions_for_problem(
        solutions_table, best_solution, meta_problem.peek())
  return widgets.VBox([widgets.HBox(items), solutions_table])


def _update_solutions_for_problem(table, best_solution, problem):
  solutions = problem.solutions()
  if solutions.peek():
    best_solution.value = solutions.peek()
  headers = ['score', 'solution', 'notes']
  data = []
  for solution, score in solutions.items():
    data.append([
      round(score, 3),
      _format_solution(solution),
      '<br />'.join(problem.notes_for(solution))
    ])
  table.update_data(data, headers=headers)


def _observable_for_widget(widget):
  def subscribe(observer):
    def _on_change(change):
      observer.on_next(change['new'])

    widget.observe(_on_change, names='value')

  return rx.AnonymousObservable(subscribe)


def _format_solution(solution):
  return '<pre>%s</pre>' % solution.replace('\n', '<br />')
