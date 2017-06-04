from ipywidgets import widgets


def TableWidget(data=None, headers=None):
  """Factory for IPython widgets, pretending to be real widget."""
  widget = widgets.HTML()

  def update_data(data=None, headers=None):
    result = [
      '<div class="rendered_html jp-RenderedHTMLCommon">',
      '  <table>',
    ]
    if headers:
      result.extend([
        '<thead>',
        '  <tr>',
      ])
      for header in headers:
        result.append('<th>%s</th>' % header)
      result.extend([
        '  </tr>',
        '</thead>',
      ])
    if data:
      for row in data:
        result.append('<tr>')
        for datum in row:
          result.append('<td>%s</td>' % datum)
        result.append('</tr>')
    result.extend([
      '  </table>'
      '</div>',
    ])
    widget.value = ''.join(result)

  widget.update_data = update_data
  widget.update_data(data=data, headers=headers)
  return widget
