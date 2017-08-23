# coding: utf8
from collections import namedtuple
import os
from unittest import TestCase

from oopycql.query import CypherQuery


class RegexForParameterFindingTestCase(TestCase):
    TestParamFinderQuery = namedtuple('TestParamFinderQuery', 'query params')
    TEST_QUERIES = [
        TestParamFinderQuery(
            'MATCH (a:Node) WHERE a.name = {param} AND a.woof = {param2}',
            {'param', 'param2'}),
        TestParamFinderQuery(
            'MATCH (a:Node) WHERE a.name = {some_param} AND a.woof = {param2}',
            {'param2', 'some_param'}),
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
            'MATCH (a:Node { name: $héllo })',
            {'héllo'}),
        TestParamFinderQuery(
            'MATCH (a) WHERE a.p = { a¢1轉123 } RETURN *',
            {'a¢1轉123'}),
        TestParamFinderQuery(
            'MATCH (a) WHERE a.p = { a¢1轉123 } '
            'AND a.q <> { a¢1轉123 } RETURN *',
            {'a¢1轉123'}),
        TestParamFinderQuery(
            'MATCH (a) WHERE a.p = { a¢1轉123 } '
            'AND a.q <> $a¢1轉123 RETURN *',
            {'a¢1轉123'}),
    ]

    def test_all_test_queries(self):
        for q in self.TEST_QUERIES:
            ps = CypherQuery.find_params_in_query(q.query)
            print('Testing for {0}'.format(q.query))
            print(str(ps).encode('utf8'))
            assert len(ps) == len(q.params)
            assert ps == q.params


class CypherQueryInterfaceTestCase(TestCase):
    """Check the interface for various debugging and inheritance
    purposes"""

    q0 = 'MATCH (n) RETURN (n)'
    """Example query used in this test."""
    q1 = 'MATCH (n:SomeLabel) WHERE n.some_property = {some_param} RETURN n'
    """Example query used in this test."""

    def test_init_constructor(self):
        cq = CypherQuery(self.q0)
        assert cq._query == self.q0

    def test_repr_shows_query(self):
        assert self.q0[:37] in repr(CypherQuery(self.q0))

    def test_repr_shows_ellipsis(self):
        cq = CypherQuery(self.q1)
        assert self.q1[:37] in repr(cq)
        assert repr(cq)[-6:-3] == '...'

    def test_str_interface(self):
        assert str(CypherQuery(self.q0)) == self.q0

    def test_param_finder(self):
        cq = CypherQuery(self.q1)
        print(cq, cq.params, CypherQuery.find_params_in_query(self.q1))
        p = cq.params
        assert 'some_param' in p
        assert p == cq._params


class CypherQueryFileConstructorTestCase(TestCase):
    """Check that CypherQuery objects can be loaded from a file.
    """
    def test_file_constructor(self):
        cq = CypherQuery.from_file('fixtures/q1.cql')
        assert str(cq) == 'MATCH (n) RETURN COUNT(n)\n'

    def test_file_constructor(self):
        rt = os.path.dirname(os.path.abspath(__file__))
        cq = CypherQuery.from_file('fixtures/q2.cql', relative_to=rt)
        assert str(cq) == 'MATCH (n) RETURN COUNT(n) AS q2_return\n'
