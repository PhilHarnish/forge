import numpy as np

from data.image import component
from spec.mamba import *

with description('Component'):
  with it('instantiates'):
    expect(calling(component.Component, np.zeros((3, 4)))).to(
        be_a(component.Component))

  with it('hashes same things consistently'):
    a = component.Component(np.zeros((3, 4)))
    b = component.Component(np.zeros((3, 4)))
    expect(hash(a)).to(equal(hash(b)))

  with it('hashes different things differently'):
    a = component.Component(np.zeros((3, 4)))
    b = component.Component(np.zeros((4, 3)))
    expect(hash(a)).not_to(equal(hash(b)))

  with description('repr'):
    with it('omits unspecified information'):
      expect(repr(component.Component(np.zeros((3, 3))))).to(
          equal('Component(<image>)'))

    with it('includes specified labels'):
      data = np.zeros((3, 3))
      labels = {'key': 'value'}
      expect(repr(component.Component(data, labels=labels))).to(
          equal('''Component(<image>, labels={'key': 'value'})'''))

  with description('str'):
    with it('omits unspecified information'):
      expect(str(component.Component(np.zeros((3, 3))))).to(equal('{}'))

    with it('includes specified labels'):
      data = np.zeros((3, 3))
      labels = {'key': 'value'}
      expect(str(component.Component(data, labels=labels))).to(
          equal('''{'key': 'value'}'''))


with description('PositionedComponent'):
  with it('instantiates'):
    expect(calling(
        component.PositionedComponent, np.zeros((3, 4)), component.Offset(0, 0))
    ).to(be_a(component.PositionedComponent))

  with it('hashes same things consistently'):
    a = component.PositionedComponent(np.zeros((3, 4)), component.Offset(1, 2))
    b = component.PositionedComponent(np.zeros((3, 4)), component.Offset(1, 2))
    expect(hash(a)).to(equal(hash(b)))

  with it('hashes different things differently'):
    a = component.PositionedComponent(np.zeros((3, 4)), component.Offset(1, 2))
    b = component.PositionedComponent(np.zeros((3, 4)), component.Offset(3, 4))
    expect(hash(a)).not_to(equal(hash(b)))

  with description('repr'):
    with it('includes specified origin'):
      data = np.zeros((3, 3))
      offset = component.Offset(4, 5)
      expect(repr(component.PositionedComponent(data, offset=offset))).to(
          equal('PositionedComponent(<image>, offset=Offset(top=4, left=5))'))

  with description('str'):
    with it('includes specified origin'):
      data = np.zeros((3, 3))
      offset = component.Offset(4, 5)
      expect(str(component.PositionedComponent(data, offset=offset))).to(
          equal('{} @ (4, 5)'))
