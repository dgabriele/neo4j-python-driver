from collections import defaultdict
from threading import RLock

from .schema import Schema
from .relationship import Relationship
from .predicate import PredicateProperty


class Symbol(object):

    _visited_node_classes = set()
    _visited_node_classes_lock = RLock()

    def __init__(self, node_class, alias, label, props):
        assert node_class
        assert node_class.label

        self.node_class = node_class
        self.alias = alias
        self.label = label or node_class.label
        self.props = props

        self._next = None
        self._path_name = None
        self._schema = node_class.Properties()

        # init dynamic "relationship" methods
        with self._visited_node_classes_lock:
            if node_class not in self._visited_node_classes:
                self._visited_node_classes.add(node_class)
                for name in self.node_class.relationships:
                    method = self._new_relationship_method(name)
                    setattr(self.__class__, method.__name__, method)

    def _new_relationship_method(self, name):
        def method(self, symbol, props=None, name=name[:], path=None):
            copy = self.copy()
            copy._path_name = path
            relationship = self.node_class.relationships[name]
            copy._next = (relationship, symbol, props)
            return copy
        method.__name__ = name
        return method

    def __str__(self):
        return self.emit()

    def __getattr__(self, attr):
        if attr in self._schema.fields:
            return PredicateProperty(self, attr)

    def __call__(self, alias='', label='', props=''):
        alias = self.alias if alias == '' else alias
        label = self.label if label == '' else label
        props = self.props if props == '' else props
        return Symbol(self.node_class, alias, label, props)

    @property
    def path_name(self):
        return self._path_name

    @property
    def next(self):
        return self._next

    def copy(self):
        return Symbol(self.node_class, self.alias, self.label, self.props)

    def emit(self):
        ret_str = ''
        name_str = self.alias or ''
        if self.label:
            ret_str += '({}:{})'.format(name_str, self.label)
        else:
            ret_str += '({})'
        if self._next is not None:
            rel, sym, props = self._next
            ret_str += '{}{}'.format(rel.emit(props), sym.emit())
        if self._path_name:
            ret_str = '{} = {}'.format(self._path_name, ret_str)
        return ret_str
