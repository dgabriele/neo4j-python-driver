from neo4j.orm import Cypher, Relationship, Node
from neo4j.orm.schema import Schema, Int, Str, Dict, List

class Company(Node):
    class Properties(Schema):
        name = Str()
        company_type = Str(load_from='type')
        locations = List(Dict)
        industries = List(Dict)


if __name__ == '__main__':
    from neo4j.v1 import GraphDatabase, basic_auth

    url = "bolt://localhost:7687"
    driver = GraphDatabase.driver(url, auth=basic_auth("neo4j", "tempus"))
    session = driver.session()

    company_data = [
        {'name': 'a'},
        {'name': 'b'},
        {'name': 'c'},
        ]

    c = Company.symbol('c')

    for data in company_data:
        Cypher(session).merge(c(props=data)).run()
