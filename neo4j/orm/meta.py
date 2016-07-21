import re
import base36

from threading import Lock

from .relationship import Relationship


class neo4j_type(type):
    def __new__(cls, name, bases, dct):
        if bases[0] is not object:
            cls.ensure_properties_schema(dct)
            cls.collect_relationships(dct)
            cls.build_node_label(dct, name)

            prop = property(lambda self: 5)
            dct['test'] = prop

        return type.__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        if bases[0] is not object:
            cls.build_next_symbol_name_static_method()
        return type.__init__(cls, name, bases, dct)

    def build_node_label(dct, cls_name):
        if 'labels' in dct:
            dct['label'] = ':'.join(cls.labels) or name
        else:
            dct['labels'] = [cls_name]
            dct['label'] = cls_name

    def ensure_properties_schema(dct):
        props_schema_cls = dct.get('Properties')
        assert props_schema_cls is not None

    def collect_relationships(dct):
        dct['relationships'] = {
                k: v for k, v in dct.items()
                if isinstance(v, Relationship)
                }

    def build_next_symbol_name_static_method(cls):
        cls._name_counter = 1
        cls._name_counter_lock = Lock()

        def next_symbol_name():
            with cls._name_counter_lock:
                n = cls._name_counter
                cls._name_counter += 1
                return '{}_{}'.format(
                        re.sub(r'\W', '', cls.label.lower()),
                        base36.dumps(n))

        cls.next_symbol_name = next_symbol_name
