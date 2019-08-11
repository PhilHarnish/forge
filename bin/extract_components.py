import collections
import glob
import os
import pickle
from typing import Dict, Iterator, List, NamedTuple, Tuple

import cv2
import numpy as np

from data import data
from data.image import component
from puzzle.problems.image import image_problem
from puzzle.puzzlepedia import prod_config

prod_config.init()


_CLASSIFIED_COMPONENTS = data.project_path('data/grid/classified_components')
_CLASSIFIED_MAX_WIDTH = 720
_COMPONENT_SCRATCH = data.project_path('data/grid/components.pkl')
_COMPONENT_INDEX = data.project_path('data/grid/component_index.pkl')
_GRID_FILE_PATTERN = data.project_path('data/grid/original/*.png')
_IMSHOW_TITLE = 'component'
_TODO = {
}
_FOCUS = {
}


class ClassifiedComponent(NamedTuple):
  classification: str
  component: component.Component


AllComponents = Dict[int, ClassifiedComponent]
ComponentPosition = Tuple[int, int]


def images() -> Iterator[np.ndarray]:
  for filename in sorted(glob.glob(_GRID_FILE_PATTERN)):
    yield (
      os.path.basename(filename),
      cv2.imread(filename, flags=cv2.IMREAD_UNCHANGED))


def image_problems() -> Iterator[image_problem.ImageProblem]:
  for name, image in images():
    if _FOCUS and name not in _FOCUS:
      continue
    if name in _TODO:
      print('Skipping unsupported image:', name)
      continue
    print('Working on:', name)
    yield image_problem.ImageProblem(name, image)


def read_classified() -> AllComponents:
  if not os.path.exists(_COMPONENT_SCRATCH):
    return {}
  all_components = pickle.load(open(_COMPONENT_SCRATCH, 'rb'))
  print('Loaded %s' % len(all_components))
  return all_components


def verify_classified(all_components: AllComponents) -> None:
  classified_index = collections.defaultdict(list)
  for classification, c in all_components.values():
    classified_index[classification].append(c)
  print('Click to erase incorrect classifications')
  print('Press any key to continue')
  for classification, components_list in sorted(
      classified_index.items(), key=lambda x: x[0]):
    if classification == '-':
      continue
    print('Classification:', classification)
    output, positions = illustrate_classified_components(components_list)
    positioned_components = [
      (position, c) for position, c in zip(positions, components_list)]
    if not interactive_click_to_remove(
        output, positioned_components, all_components):
      break


def interactive_click_to_remove(
    image: np.ndarray,
    positioned_components: List[Tuple[ComponentPosition, component.Component]],
    all_components: AllComponents) -> bool:
  def on_mouse_click(event: int, x: int, y: int, flags: int, param: None):
    del flags, param
    if event != cv2.EVENT_LBUTTONUP:
      return
    for (c_x, c_y), c in positioned_components:
      if x < c_x or y < c_y:
        continue
      height, width = c.image.shape
      if x > c_x + width or y > c_y + height:
        continue
      del all_components[hash(c)]
      image[c_y:c_y + height, c_x:c_x + width] = 128

  cv2.namedWindow(_IMSHOW_TITLE)
  cv2.setMouseCallback(_IMSHOW_TITLE, on_mouse_click)
  while True:
    cv2.imshow(_IMSHOW_TITLE, image)
    key = cv2.waitKey(250) & 0xFF
    if key == 27:
      return False
    elif key != 255:
      break
  return True


def write_classified(all_components: AllComponents) -> None:
  print('Writing %s' % len(all_components))
  pickle.dump(
      all_components,
      open(_COMPONENT_SCRATCH, 'wb'),
      protocol=pickle.HIGHEST_PROTOCOL)
  index = {}
  for k, v in all_components.items():
    if v.classification == '-':
      continue
    index[k] = component.Component(v.component.image, labels={
      'symbol': v.classification,
    })
  pickle.dump(
      index,
      open(_COMPONENT_INDEX, 'wb'),
      protocol=pickle.HIGHEST_PROTOCOL)


def classify(all_components: AllComponents) -> None:
  manual_mode = False
  shift = False
  for i in image_problems():
    unclassified_components = list(i.get_components())
    i = 0
    while i < len(unclassified_components):
      c = unclassified_components[i]
      hash_id = hash(c)
      if hash_id in all_components:
        if not manual_mode:
          print('component already identified:',
              all_components[hash_id].classification)
          i += 1
          continue
        classification = all_components[hash_id].classification
      else:
        classification = None
      print('hash id:', hash_id, classification)

      cv2.imshow(_IMSHOW_TITLE, c.image)
      code = cv2.waitKey(0)
      key = chr(code & 0xFF)
      if code == 27:  # ESC
        return
      elif code == 0:
        shift = True
        continue
      elif code == 32:  # SPACE
        all_components[hash_id] = ClassifiedComponent(
            input('classification:'), c)
        manual_mode = False
      elif code == 44:  # <
        i -= 1
        manual_mode = True
        continue
      elif code == 46:  # >
        i += 1
        manual_mode = True
        continue
      elif code == 45:  # -?
        print('ignoring')
        all_components[hash_id] = ClassifiedComponent('-', c)
        manual_mode = False
        shift = False
      elif key.isalnum():
        if shift:
          key = key.upper()
        all_components[hash_id] = ClassifiedComponent(key, c)
        manual_mode = False
        shift = False
      else:
        print('unrecognized:', code)
      i += 1


def illustrate_all_classified(all_classified: AllComponents) -> None:
  classified_index = collections.defaultdict(list)
  for classification, c in all_classified.values():
    classified_index[classification].append(c)
  for classification, components_list in classified_index.items():
    output, _ = illustrate_classified_components(components_list)
    write_classified_components(output, classification)


def illustrate_classified_components(
    all_components: List[component.Component]
) -> Tuple[np.ndarray, List[ComponentPosition]]:
  all_components = list(sorted(
      all_components, key=lambda c: c.image.shape[0] * c.image.shape[1],
      reverse=True))
  position_information = []
  total_width = 0
  max_row_height = 0
  cursor_x = 0
  cursor_y = 0
  for c in all_components:
    height, width = c.image.shape
    if cursor_x + width > _CLASSIFIED_MAX_WIDTH:
      total_width = max(total_width, cursor_x)
      cursor_x = 0
      cursor_y += max_row_height
      max_row_height = 0
    position_information.append((cursor_x, cursor_y))
    cursor_x += width
    max_row_height = max(max_row_height, height)
  total_width = max(total_width, cursor_x) + 8  # Arbitrary padding.
  total_height = cursor_y + max_row_height

  shape = (total_height, total_width)
  output = np.zeros(shape, dtype=np.uint8)
  for c, (x, y) in zip(all_components, position_information):
    height, width = c.image.shape
    output[y:y + height, x:x + width] = c.image
  return output, position_information


def write_classified_components(
    output: np.ndarray, classification: str) -> None:
  filename = os.path.join(_CLASSIFIED_COMPONENTS, '%s.png' % classification)
  cv2.imwrite(filename, output)


def main() -> None:
  already_classified = read_classified()
  verify_classified(already_classified)
  classify(already_classified)
  write_classified(already_classified)
  illustrate_all_classified(already_classified)

main()
