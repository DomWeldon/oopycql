from collections import namedtuple
from unittest import TestCase

from oopycql.query import CypherQuery


class RegexForParameterFindingTestCase(TestCase):
    TestParamFinderQuery = namedtuple('TestParamFinderQuery', 'query params')
    TEST_QUERIES = [
        TestParamFinderQuery(
            'MATCH (a:Node) WHERE a.name = {param} AND a.woof = {param2}',
            {'param', 'param2'}),
        TestParamFinderQuery(
            'MATCH (a:Node) WHERE a.name = $param',
            {'param'}),
        TestParamFinderQuery(
            'MATCH (a:Node) WHERE a.name = $`silly param`',
            {'silly param'}),
        TestParamFinderQuery(
            'MATCH (a:Node) WHERE a.name = { `ridiculous param!` }',
            {'ridiculous param!'}),
        TestParamFinderQuery(
            'MATCH (a:Node) WHERE a.name = { a }',
            {'a'}),
        TestParamFinderQuery(
            'MATCH (a:Node) WHERE a.name = { 1 }',
            {'1'}),
        TestParamFinderQuery(
            'MATCH (a:Node { name: { param } })',
            {'param'}),
        TestParamFinderQuery(
            'MATCH (a:Node { name: $param })',
            {'param'}),
        TestParamFinderQuery(
            u'MATCH (a:Node { name: $héllo })',
            {u'héllo'}),
        TestParamFinderQuery(
            u'MATCH (a) WHERE a.p = { a¢1轉123 } RETURN *',
            {u'a¢1轉123'}),
        TestParamFinderQuery(
            u'MATCH (a) WHERE a.p = { a¢1轉123 } '
            u'AND a.q <> { a¢1轉123 } RETURN *',
            {u'a¢1轉123'}),
        TestParamFinderQuery(
            u'MATCH (a) WHERE a.p = { a¢1轉123 } '
            u'AND a.q <> $a¢1轉123 RETURN *',
            {u'a¢1轉123'}),
    ]

    def test_all_test_queries(self):
        for q in self.TEST_QUERIES:
            ps = CypherQuery.find_params_in_query(q.query)
            print('Testing for {0}'.format(q.query))
            print(ps)
            assert len(ps) == len(q.params)
            assert ps == q.params


class CypherQueryInterfaceTestCase(TestCase):
    """Check the interface for various debugging and inheritance
    purposes"""

    q = 'MATCH (n) RETURN (n)'
    """Example query used in this test."""

    def test_init_constructor(self):
        cq = CypherQuery(self.q)
        assert cq._query == self.q

    def test_repr_shows_query(self):
        assert self.q[:37] in repr(CypherQuery(self.q))

    def test_str_interface(self):
        assert str(CypherQuery(self.q)) == self.q
