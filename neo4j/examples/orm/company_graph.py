import json
import types
import random
import uuid
import re

from pprint import pprint

from neo4j.orm import Cypher, Relationship, Node
from neo4j.orm.schema import Schema, Int, Str, Dict, List, Number
from neo4j.orm.util import get_driver


# ---------------------------------------------------------------
def new_session(reinit=False):
    session = get_driver().session()
    if reinit:
        Cypher(session).match('(u) DETACH').delete('u').run()
        initialize(session, load_json())
    return session


def load_json():
    company_data = []
    with open('companies.json') as fin:
        return json.load(fin)


def initialize(session, data):
    industries = {}
    for x in data['industries']:
        industries[x['id']] = Industry.symbol(props=x)

    sectors = {}
    for x in data['sectors']:
        sectors[x['id']] = Sector.symbol(props=x)

    regions = {}
    for x in data['regions']:
        regions[x['id']] = GeographicRegion.symbol(props=x)

    cities = {}
    for x in data['cities']:
        cities[x['id']] = GeographicCity.symbol(props=x)

    states = {}
    for x in data['states']:
        states[x['id']] = GeographicState.symbol(props=x)

    Cypher(session)\
            .create(industries, sectors, regions, cities, states)\
            .run()

    ##
    ## Create industry -> sector relationships
    ##

    relationships = []
    visited_sectors = set()
    visited_industries = set()
    for industry in industries.values():
        sector_id = industry.props['sector_id']
        sector = sectors[sector_id]
        if sector_id not in visited_sectors:
            visited_sectors.add(sector_id)
        else:
            sector = sector(label=None, props=None)

        indusry_id = industry.props['id']
        industry = industry(label=None)
        if indusry_id in visited_industries:
            industry = industry(props=None)
        else:
            visited_industries.add(indusry_id)

        relationships.append(industry.in_sector(sector))

    for industry in industries.values():
        industry_id = industry.props['id']
        sector_id = industry.props['sector_id']

        industry = Industry.symbol()
        sector = Sector.symbol()

        cypher = Cypher(session)\
                .match(industry, sector)\
                .where(industry.id == industry_id, sector.id == sector_id)\
                .create(industry(label=None).in_sector(sector(label=None)))

        cypher.run()

    for x in data['companies'][:100]:
        loations = x.pop('locations')
        industry_ids = x.pop('industry_ids')
        if industry_ids:
            company = Company.symbol(props=x)
            industry = Industry.symbol()
            cypher = Cypher(session)\
                    .match(industry)\
                    .where(industry.id.is_in(industry_ids))\
                    .create(company)\
                    .create(company(label=None, props=None)\
                        .in_industry(industry(label=None)))

            res = cypher.run()


# ---------------------------------------------------------------
class Company(Node):
    class Properties(Schema):
        name = Str()
        company_type = Str(load_from='type', allow_none=True)
        locations = List(Dict)
        industries = List(Dict)
        revenue = Number()

    has_address = Relationship('has_address->')
    in_sector = Relationship('in_sector->')
    in_industry = Relationship('in_industry->')


class Sector(Node):
    class Properties(Schema):
        id = Int()
        name = Str()

    has_industry = Relationship('has_industry->')

class Industry(Node):
    class Properties(Schema):
        id = Int()
        name = Str()

    in_sector = Relationship('in_sector->')


class GeographicState(Node):
    class Properties(Schema):
        id = Str()
        name = Str()

    contains_city = Relationship('contains_city->')

class GeographicCity(Node):
    class Properties(Schema):
        name = Str()

    in_state = Relationship('in_state->')


class GeographicRegion(Node):
    class Properties(Schema):
        code = Str()
        name = Str()

    contains_city = Relationship('contains->')
    contains_state = Relationship('contains->')
    has_industry = Relationship('has_industry->')
    has_sector = Relationship('has_sector->')


class Address(Node):
    class Properties(Schema):
        street_1 = Str()
        street_2 = Str()
        state = Str()
        city = Str()
        postal_code = Str()

    in_city  = Relationship('in_city->')
    in_state = Relationship('in_state->')
    in_region = Relationship('in_region->')

# ---------------------------------------------------------------
class Search(object):
    class Parameters(Schema):
        search_str = Str(required=True)
        created_from = Int()
        updated_from = Int()
        company_types = List(Str)
        industry_ids = List(Int)
        sector_ids = List(Int)
        state_codes = List(Str)
        cities = List(Str)
        min_revenue = Int()
        max_revenue = Int()


    parameters_schema = Parameters()

    def __init__(self, session):
        self.session = session

    def full_text(self, params):
        self.parameters_schema.validate(params)

        company = Company.symbol()
        industry = Industry.symbol()
        sector = Sector.symbol()
        state = GeographicState.symbol()
        city = GeographicCity.symbol()
        addr = Address.symbol(var=None, label=None)

        relationships, predicates = [], []

        predicates.append(company.name.regex(params['search_str']))

        if 'industry_ids' in params:
            relationships.append(company.in_industry(industry))
            predicates.append(industry.id.is_in(params['industry_ids']))

        if 'sector_ids' in params:
            relationships.append(company.in_sector(sector))
            predicates.append(sector.id.is_in(params['sector_ids']))

        if 'state_codes' in params:
            relationships.append(company.has_address(addr).in_state(state))
            predicates.append(state.name.is_in(params['state_codes']))

        if 'cities' in params:
            relationships.append(company.has_address(addr).in_city(city))
            predicates.append(city.name.is_in(params['cities']))

        if 'min_revenue' in params:
            predicates.append(company.revenue >= params['min_revenue'])

        if 'max_revenue' in params:
            predicates.append(company.revenue <= params['max_revenue'])

        cypher = Cypher(self.session)\
                .match(company, relationships)\
                .where(predicates)\
                .ret(company)

        print(cypher)
        return cypher.run()


# ---------------------------------------------------------------
if __name__ == '__main__':
    session = new_session(reinit=True)

    exit()

    search = Search(session)

    results = search.full_text({
        'search_str': r'(?i).*llc.*',
        'cities': ['New York'],
        })

    for rec in results:
        for x in rec:
            print(' >>> ' + x.props['name'])
