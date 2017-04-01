import os

_this_path = os.path.dirname(os.path.realpath(__file__))
_base_path = os.path.join(_this_path.split('/forge/')[0], 'forge')


def project_path(path):
  return os.path.join(_base_path, path)


def load(path, cls):
  return load_lines(_read_lines(path), cls)


def load_lines(lines, cls):
  acc = []
  last_group = None
  result = {}
  def maybe_flush_buffer():
    if acc:
      result[last_group] = cls(last_group, acc)
    return []
  for line in lines:
    line = line.rstrip('\n')
    if line.startswith('[') and line.endswith(']'):
      acc = maybe_flush_buffer()
      last_group = line.strip('[]')
    else:
      acc.append(line)
  maybe_flush_buffer()
  return result


def open_project_path(path, **kwargs):
  return open(project_path(path), **kwargs)


def _read_lines(path):
  return open_project_path(path).readlines()
