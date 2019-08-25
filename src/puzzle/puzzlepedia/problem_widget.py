from typing import ContextManager

from ipywidgets import widgets

from puzzle.constraints import constraints
from puzzle.problems import problem
from puzzle.puzzlepedia import _bind, _common, _widget_util, \
  annotation_widget, \
  debug_data_widget, meta_problem, table_widget
from puzzle.puzzlepedia._bind import widget_observable
from puzzle.steps import step

_MAX_RESULTS = 30


def ProblemWidget(mp: meta_problem.MetaProblem):
  """Factory for IPython widgets, pretending to be real widget."""
  capture = widgets.Output()
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
        interactive_information, p, capture)

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
        interactive_information, mp.peek(), capture)

  for p in mp:
    p.subscribe(_bind.callback_without_event(
        _update_solutions_for_problem, solutions_table, best_solution, p))

  return widgets.VBox(
      [widgets.HBox(items), interactive_information, solutions_table, capture])


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
      _common.preformat_html(solution),
      '<br />'.join(p.notes_for(solution))
    ])
  table.update_data(data, headers=headers)


def _update_interactive_information_for_problem(
    interactive_information: widgets.VBox,
    p: problem.Problem,
    capture: ContextManager):
  accordion_children = []
  steps = list(p.steps())
  for s in steps:
    step_tabs_children = []
    for group in s.constraints():
      child_constraints = []
      group_container = widgets.VBox(child_constraints)
      _update_annotations_for_group(group_container, group, capture)
      group.subscribe(_bind.callback_without_event(
          _update_annotations_for_group, group_container, group, capture))
      step_tabs_children.append(group_container)
    step_tabs = widgets.Tab(step_tabs_children)
    for i, group in enumerate(s.constraints()):
      step_tabs.set_title(i, _common.format_label(group.__class__.__name__))
    debug_data_container = widgets.VBox([])
    debug_data_accordion = widgets.Accordion([debug_data_container])
    debug_data_accordion.set_title(0, 'debug data')
    debug_data_accordion.selected_index = None
    _update_debug_data_for_problem(debug_data_container, s)
    p.subscribe(_bind.callback_without_event(
        _update_debug_data_for_problem, debug_data_container, s))
    s.subscribe(_bind.callback_without_event(
        _update_debug_data_for_problem, debug_data_container, s))
    step_tabs = widgets.VBox([step_tabs, debug_data_accordion])
    accordion_children.append(step_tabs)
  accordion = widgets.Accordion(children=accordion_children)
  for i, s in enumerate(steps):
    accordion.set_title(i, _common.format_label(str(s)))
  interactive_information.children = (accordion,)


def _update_annotations_for_group(
    annotations_container: widgets.VBox,
    group: constraints.Constraints,
    capture: ContextManager) -> None:
  children = []
  for key, value, annotation in group:
    children.append(annotation_widget.AnnotationWidget(
        annotation, group, key, value, capture))
  _widget_util.merge_assign_children(annotations_container, children)


def _update_debug_data_for_problem(
    debug_data_container: widgets.VBox, s: step.Step
):
  # TODO: Diff.
  debug_widget = debug_data_widget.DebugDataWidget(s)
  debug_data_container.children = (debug_widget,)
