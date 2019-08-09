import re

_CAMEL_CASE_RE = re.compile(r'([a-z])([A-Z])')


def format_label(label: str) -> str:
  return _CAMEL_CASE_RE.sub(r'\1 \2', label).lower().replace('_', ' ')


def format_solution_html(solution: str) -> str:
  return '<pre>%s</pre>' % solution.replace('\n', '<br />')
