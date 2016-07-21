import re
import json

from .constants import DIR_IN, DIR_OUT, DIR_NONE


class Relationship(object):
    RE_PROP_NAME = re.compile(r'"(\w+?)":')

    def __init__(self, label=None, direction=None):
        self.label = label
        self.direction = direction or DIR_NONE

    def emit(self, props=None):
        if self.label or props:
            if props:
                props_str = self.RE_PROP_NAME.sub(r'\1:', json.dumps(props))
            else:
                props_str = ''
            edge_label = '[{}{}]'.format(
                    ':' + self.label if self.label else '',
                    ' ' + props_str if props else '')
        else:
            edge_label = ''

        if self.direction == DIR_OUT:
            return '-{}->'.format(edge_label)
        elif self.direction == DIR_IN:
            return '<-{}'.format(edge_label)
        elif self.direction == DIR_NONE:
            return '-{}-'.format(edge_label)

        raise ValueError('invalid relationship direction')
