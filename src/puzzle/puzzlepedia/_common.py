import html
import re

_CAMEL_CASE_RE = re.compile(r'([a-z])([A-Z])')


def format_label(label: str) -> str:
  return _CAMEL_CASE_RE.sub(r'\1 \2', label).lower().replace('_', ' ')


def preformat_html(solution: str) -> str:
  return '<pre>%s</pre>' % html.escape(solution).replace('\n', '<br />')
