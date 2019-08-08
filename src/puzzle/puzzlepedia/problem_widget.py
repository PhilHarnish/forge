from ipywidgets import widgets

from puzzle.problems import problem
from puzzle.puzzlepedia import _bind, annotation_widget, debug_data_widget, \
  meta_problem, table_widget
from puzzle.puzzlepedia._bind import widget_observable
from puzzle.puzzlepedia._common import format_label, format_solution_html

_MAX_RESULTS = 30


def ProblemWidget(mp: meta_problem.MetaProblem):
  """Factory for IPython widgets, pretending to be real widget."""
  items = []
  options = {}
  for p in mp:
    # 'p' is instance of problem.Problem.
    options[p.kind] = p
  # Dropdown.
  dropdown = widgets.Dropdown(options=options)
  items.append(dropdown)
  dropdown_source = widget_observable(dropdown)

  # Interactive information appears between dropdown + solution and the
  # table of solutions.
  interactive_information = widgets.VBox([])
  # Best solution.
  best_solution = widgets.Text()
  items.append(best_solution)

  def _on_problem_kind_change(p: problem.Problem) -> None:
    _update_solutions_for_problem(solutions_table, best_solution, p)
    _update_interactive_information_for_problem(
        interactive_information, p)

  dropdown_source.subscribe(_on_problem_kind_change)
  best_solution_source = widget_observable(best_solution)

  def _on_best_solution_change(solution: str) -> None:
    mp.solution = solution

  best_solution_source.subscribe(_on_best_solution_change)
  solutions_table = table_widget.TableWidget()
  if mp.peek():
    _update_solutions_for_problem(
        solutions_table, best_solution, mp.peek())
    _update_interactive_information_for_problem(
        interactive_information, mp.peek())

  for p in mp:
    p.subscribe(_bind.callback_without_event(
        _update_solutions_for_problem, solutions_table, best_solution, p))

  return widgets.VBox(
      [widgets.HBox(items), interactive_information, solutions_table])


def _update_solutions_for_problem(
    table: table_widget.TableWidget,
    best_solution: widgets.Text,
    p: problem.Problem) -> None:
  solutions = p.solutions()
  if solutions.peek():
    best_solution.value = solutions.peek()
  headers = ['score', 'solution', 'notes']
  data = []
  for i, (solution, score) in enumerate(solutions.items()):
    if i >= _MAX_RESULTS:
      break
    data.append([
      round(score, 3),
      format_solution_html(solution),
      '<br />'.join(p.notes_for(solution))
    ])
  table.update_data(data, headers=headers)


def _update_interactive_information_for_problem(
    interactive_information: widgets.VBox, p: problem.Problem):
  accordion_children = []
  steps = list(p.steps())
  for step in steps:
    step_tabs_children = []
    for group in step.constraints():
      child_constraints = []
      for key, value, annotation in group:
        child_constraints.append(
            annotation_widget.AnnotationWidget(annotation, group, key, value))
      step_tabs_children.append(widgets.VBox(child_constraints))
    step_tabs = widgets.Tab(step_tabs_children)
    for i, group in enumerate(step.constraints()):
      step_tabs.set_title(i, format_label(group.__class__.__name__))
    try:
      # TODO: Diff.
      debug_widget = debug_data_widget.DebugDataWidget(step)
      step_tabs = widgets.VBox([step_tabs, debug_widget])
    except NotImplementedError:
      pass  # No debug data for this step.
    accordion_children.append(step_tabs)
  accordion = widgets.Accordion(children=accordion_children)
  for i, step in enumerate(steps):
    accordion.set_title(i, format_label(str(step)))
  interactive_information.children = (accordion,)
