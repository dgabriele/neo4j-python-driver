from neo4j.orm import Cypher, Relationship, Node
from neo4j.orm.schema import Schema, Int, Str, Dict, List, Number
from neo4j.orm.util import get_driver

class User(Node):
    class Properties(Schema):
        id = Str()
        name = Str()
        age = Int()

    in_company = Relationship('IN_COMPANY->')


class Company(Node):
    class Properties(Schema):
        id = Str()
        name = Str()
        company_type = Str()
        description = Str()

    has_member = Relationship('HAS_MEMBER->')


if __name__ == '__main__':
    session = get_driver().session()

    user = User.symbol()
    company = Company.symbol()

    Cypher(session).match(user)
