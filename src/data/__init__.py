import os

_this_path = os.path.dirname(os.path.realpath(__file__))
_base_path = os.path.join(_this_path.split('/forge/')[0], 'forge')

def project_path(path):
  return os.path.join(_base_path, path)
