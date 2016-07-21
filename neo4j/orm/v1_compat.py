import neo4j.v1.types as v1_types

from .node import Node


class StatementResultProxy(object):
    def __init__(self, cypher, statement_result):
        self.cypher = cypher
        self.statement_result = statement_result

    def __getattr__(self, name):
        return getattr(self.result, name)

    def __iter__(self):
        for rec in self.statement_result:
            orm_objs = []
            for v1_obj in rec.values():
                if isinstance(v1_obj, v1_types.Node):
                    orm_cls = self.cypher.v1_type_map[list(v1_obj.labels)[0]]
                    orm_objs.append(self.from_v1_node(v1_obj))
                else:
                    raise NotImplementedError()
            yield orm_objs

    @staticmethod
    def from_v1_node(node_class, v1_node):
        return node_class(
                label='|'.join(v1_node.labels),
                props=v1_node.properties,
