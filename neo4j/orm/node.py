from .meta import neo4j_type
from .symbol import Symbol

class Node(object, metaclass=neo4j_type):

    @classmethod
    def symbol(cls, alias='', label=None, props=None):
        # autogenerate a variable name. we use '' instead of None,
        # and we use None to indicate that we do not want a variable name
        if alias == '':
            alias = cls.next_symbol_name()

        return Symbol(cls, alias=alias, label=label, props=props)
