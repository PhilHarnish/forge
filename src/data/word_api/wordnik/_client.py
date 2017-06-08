import urllib.parse

from wordnik import swagger

from data import data

_CLIENT = None


class _Config(object):
  def __init__(self, name, lines):
    self.name = name
    self.value = lines[0]


class _Client(swagger.ApiClient):
  def __init__(self, config):
    super(_Client, self).__init__(
        apiKey=config['KEY'].value, apiServer=config['URL'].value)

  def toPathValue(self, obj):
    """Convert a string or object to a path-friendly value.

    Patches implementation from parent.
    Args:
        obj -- object or string value
    Returns:
        string -- quoted value
    """
    if type(obj) == list:
      return ','.join(urllib.parse.quote(i) for i in obj)
    else:
      return urllib.parse.quote(str(obj))


def get_client():
  global _CLIENT
  if _CLIENT is None:
    # This file is not committed but looks like this:
    #   [URL]
    #   http://api.wordnik.com/v4
    #
    #   [KEY]
    #   KEY_HERE
    config = data.load('data/_wordnik_credentials.txt', _Config)
    _CLIENT = _Client(config)
  return _CLIENT
