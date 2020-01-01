#!/usr/bin/env python
# coding: utf-8

from .flipping_aztecdiamond import *
from sage_widget_adapters.graphs.graph_grid_view_adapter import GraphGridViewAdapter
from sage_combinat_widgets.grid_view_widget import GridViewWidget, ButtonCell, BlankButton, styled_button_cell
from ipywidgets import Layout
from traitlets import dlink, HasTraits, Bool
from contextlib import contextmanager

smallblyt = Layout(width='12px',height='12px', margin='0', padding='0')


class FlippingDominosAdapter(GraphGridViewAdapter):

    remove_cell = None

    def set_cell(self, obj, pos, val, dirty={}):
        r"""
        When we click on a graph cell,
        we prepare a possible flip
        or we try to complete the flip if it has been prepared previously
        """
        # Find out the relevant matching for 'pos'
        d1 = obj.domino_for_position(pos)
        if dirty: # if i'm a neighbor, then flip and return a new obj ; else return an error
            # Consider the relevant matching(s)
            for p in dirty:
                if not dirty[p]: # check this position is pressed
                    continue
                d2 = obj.domino_for_position(p)
                if d2 == d1 or not d2 in d1.neighbors():
                    continue
                if d2 in d1.neighbors():
                    # Do the flip
                    obj.flip(d1, d2)
                    return obj
            return Exception("Please select a second domino!")
        else:
            return Exception("Please select a second domino!")


class ddlink(dlink):
    """Double directional link with logic = or/and/none.
    Double_source is a tuple of (source, target) tuples
    Usage: b1 = Button(description = 'B1')
           b2 = Button(description = 'B2')
           b3 = Button(description = 'B3')
           dl = ddlink(((b1, 'value'), (b2, 'value')), (b3, 'value'))
    """
    updating = False

    def __init__(self, double_source, target, logic=None, set_at_init=True):
        self.validate_tuple(target)
        self.logic = logic
        for source in double_source:
            self.validate_tuple(source)
        try:
            if set_at_init:
                if self.logic == 'and':
                    setattr(target[0], target[1],
                            getattr(double_source[0][0], double_source[0][1]) \
                            and getattr(double_source[1][0], double_source[1][1]))
                else:
                    setattr(target[0], target[1],
                            getattr(double_source[0][0], double_source[0][1]) \
                            or getattr(double_source[1][0], double_source[1][1]))
            else:
                pass
        finally:
            for source in double_source:
                source[0].observe(self._update, names=source[1])
                source[0].observe(self._update, names=source[1])
        self.target = target
        self.double_source = double_source
        self.intermediate_value = False # False / True / source.tooltip

    def __repr__(self):
        if self.double_source or self.target:
            return "A double directional link from sources=%s to target='%s'" % (self.double_source, self.target)
        return "None"

    def validate_tuple(self, t):
        if not len(t) == 2:
            raise TypeError("Each linked traitlet must be specified as (HasTraits, 'trait_name'), not %r" % t)
        obj, trait_name = t
        if not isinstance(obj, HasTraits):
            raise TypeError("Each object must be HasTraits, not %r" % type(obj))
        if not trait_name in obj.traits():
            raise TypeError("%r has no trait %r" % (obj, trait_name))

    @contextmanager
    def _busy_updating(self):
        self.updating = True
        try:
            yield
        finally:
            self.updating = False

    def _update(self, change):
        if self.updating:
            return
        with self._busy_updating():
            if self.logic == 'and':
                if self.intermediate_value == False: # aucun bouton pressé avant
                    self.intermediate_value = change.new
                elif self.intermediate_value == True: # 2 boutons pressés avant
                    setattr(self.target[0], self.target[1], change.new)
                    if change.new == False:
                        # prendre le tooltip de l'autre bouton
                        for s in self.double_source:
                            if s[0].tooltip != change.owner.tooltip:
                                self.intermediate_value = s[0].tooltip
                elif self.intermediate_value != change.owner.tooltip: # l'autre bouton a été pressé avant
                    setattr(self.target[0], self.target[1], change.new)
                    self.intermediate_value = change.new
            elif self.logic == 'or':
                if change.new == True:
                    setattr(self.target[0], self.target[1], True)
                    if self.intermediate_value == False:
                        self.intermediate_value = change.owner.tooltip
                    elif self.intermediate_value == True:
                        pass
                    elif self.intermediate_value != change.owner.tooltip:
                        self.intermediate_value = True
                else:
                    if self.intermediate_value != True:
                        setattr(self.target[0], self.target[1], False)
                    self.intermediate_value = False # FIXME

            else:
                setattr(self.target[0], self.target[1], change.new)

    def unlink(self):
        for source in self.double_source:
            source[0].unobserve(self._update, names=source[1])
        self.double_source, self.target = None, None

class Domino(HasTraits):
    r"""Objet non représenté en lui-même, les 2
    boutons qu'il contient étant, eux, des widgets"""
    value = Bool()

    def __init__(self, parent, b1, b2):
        """A domino has a parent widget and is made of 2 buttons"""
        super(Domino, self).__init__()
        self.geometry = DominoGeometry(b1.position, b2.position)
        self.parent = parent
        self.key = None
        self.first = b1
        self.second = b2
        self.buttons = (b1,b2)
        b1.link = dlink((b1, 'value'), (b2, 'value'))
        b2.link = dlink((b2, 'value'), (b1, 'value'))
        self.link = None
        self.direction = None
        self.orientation = None
        self.compute(None)

    def __repr__(self):
        if self.value:
            return repr(self.first) + ' -> ' + repr(self.second) + " PRESSED"
        return repr(self.first) + ' -> ' + repr(self.second)

    def compute(self, css_classes=None):
        """Compute buttons relative positions.
        Create double directional link from both buttons"""
        self.geometry.compute()
        if css_classes:
            for cl in css_classes:
                self.first.remove_class(cl)
                self.second.remove_class(cl)
            self.first.add_class(css_classes[self.geometry.index_for_display-1])
            self.second.add_class(css_classes[self.geometry.index_for_display-1])
        if self.geometry.orientation == 1:
            self.key = self.first.position
        else:
            self.key = self.second.position
        for cl in ['left','right','top','bottom']:
            self.first.remove_class(cl)
            self.second.remove_class(cl)
        if self.geometry.direction == 'horizontal':
            if self.geometry.orientation == 1:
                self.first.add_class('left')
                self.second.add_class('right')
            elif self.geometry.orientation == -1:
                self.first.add_class('right')
                self.second.add_class('left')
        elif self.geometry.direction == 'vertical':
            if self.geometry.orientation == 1:
                self.first.add_class('top')
                self.second.add_class('bottom')
            elif self.geometry.orientation == -1:
                self.first.add_class('bottom')
                self.second.add_class('top')
        self.link = ddlink(((self.first, 'value'), (self.second, 'value')), (self, 'value'), logic='and', set_at_init=False) # Fresh ddlink

    def is_pressed(self):
        """Is the domino pressed?"""
        return self.value

    def set_value(self, value):
        """Set domino value
        As we have a directional link,
        the domino value will also be set.
        """
        self.link.unlink()
        self.first.value = value
        self.second.value = value
        self.link = ddlink(((self.first, 'value'), (self.second, 'value')), (self, 'value'), logic='and', set_at_init=False) # Fresh ddlink

    def reset(self):
        """Full domino reset"""
        self.set_value(False)
        self.link.unlink()

    def flip(self, other):
        """Flip self with some neighboring domino"""
        if other == self or other.geometry == self.geometry:
            return
        self.reset()
        other.reset()
        self.geometry.flip(other.geometry)
        self.compute()
        other.compute()


def make_cell_widget_class_index(g):
    def cell_widget_class_index(pos):
        d = g.domino_for_position(pos)
        if d:
            return d.calc_index_for_display()
        return 0
    return cell_widget_class_index


class FlippingDominosWidget(GridViewWidget):
    """A widget with dominos"""

    def __init__(self, g):
        r"""
        Init a flipping dominos widget
        with flipping aztec diamond graph `g`
        """
        super(FlippingDominosWidget, self).__init__(g, adapter = FlippingDominosAdapter(),
                                            cell_layout = smallblyt,
                                            cell_widget_classes=[styled_button_cell(),
                                                                 styled_button_cell(style_name='b1'),
                                                                 styled_button_cell(style_name='b2'),
                                                                 styled_button_cell(style_name='b3'),
                                                                 styled_button_cell(style_name='b4'),
                                            ],
                                            cell_widget_class_index=make_cell_widget_class_index(g),
                                            blank_widget_class = BlankButton)
        self.css_classes = ['b1', 'b2', 'b3', 'b4']

    def draw(self):
        self.dominos = {}
        super(FlippingDominosWidget, self).draw()
        self.apply_matching(self.value.matching)

    def update(self):
        self.apply_matching(self.value.matching)
        for k,d in self.dominos.items():
            d.compute(self.css_classes)
            d.set_value(False) # unpress buttons

    def match(self, b1, b2):
        """Match buttons b1 and b2, that is: create a domino"""
        try:
            assert issubclass(b1.__class__, ButtonCell) and issubclass(b2.__class__, ButtonCell)
        except:
            raise Exception('This method requires 2 buttons!! b1 = %s, b2 = %s' % (b1, b2) )
        """Create a domino and let it do the work. NB: the key should always be top-left."""
        d = Domino(self, b1, b2)
        self.dominos[d.key] = d

    def reset(self):
        """Clear dominos and reset every button"""
        self.dominos = {}

    def apply_matching(self, matching):
        """Apply a matching"""
        self.dominos = {}
        for d in matching:
            self.match(self.children[d.first[0]].children[d.first[1]],
                       self.children[d.second[0]].children[d.second[1]])

    def set_value(self, value):
        """Need to call self.update() manually, as the change is not obvious to the observer!"""
        self.reset_dirty()
        self.update()
