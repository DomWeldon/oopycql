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
        """Check that parameters are identified correctly"""
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

    def test_str_constructor(self):
        """Check constructor using query as kwarg"""
        cq = CypherQuery(query=self.q0)
        assert cq._query == self.q0

    def test_repr_shows_query(self):
        """Check that __repr__ shows query as expected"""
        assert self.q0[:37] in repr(CypherQuery(query=self.q0))

    def test_repr_shows_ellipsis(self):
        """check that __repr__ truncates long queries"""
        cq = CypherQuery(query=self.q1)
        assert self.q1[:37] in repr(cq)
        assert repr(cq)[-5:-2] == '...'

    def test_str_interface(self):
        """Check str(cq) interface shows simple query"""
        assert str(CypherQuery(query=self.q0)) == self.q0

    def test_param_finder(self):
        """Check params property"""
        cq = CypherQuery(query=self.q1)
        print(cq, cq.params, CypherQuery.find_params_in_query(query=self.q1))
        p = cq.params
        assert 'some_param' in p
        assert p == cq._params

    def test_set_param_value(self):
        """Check params can be set using param property"""
        cq = CypherQuery(query='CREATE (a:Node) SET a += {np}')
        cq.params['np'] = {'a': True, 'b': False}
        assert cq.params['np']['a'] is True

    def test_iteration(self):
        """Check that iteration works as expected on a query"""
        q = 'CREATE (a:Node) SET a += {np}'
        cq = CypherQuery(query=q)
        cqi = list(cq)
        assert cqi[0] == q
        assert 'np' in cqi[1]


class CypherQueryFileConstructorTestCase(TestCase):
    """Check that CypherQuery objects can be loaded from a file.
    """
    def test_file_constructor(self):
        """Check constructor from file method"""
        cq = CypherQuery.from_file('fixtures/q1.cql')
        assert str(cq) == 'MATCH (n) RETURN COUNT(n)\n'

    def test_file_constructor2(self):
        """Check constructor from file with relative_to arg set"""
        rt = os.path.dirname(os.path.abspath(__file__))
        cq = CypherQuery.from_file('fixtures/q2.cql', relative_to=rt)
        assert str(cq) == 'MATCH (n) RETURN COUNT(n) AS q2_return\n'

    def test_from_module_constructor(self):
        """Check method to construct using query file from current
        module"""
        cq = CypherQuery.from_module('query')
        assert str(cq) == 'MATCH (n) RETURN COUNT(n)\n'

    def test_module_new(self):
        """Check __new__ method imports from a module using an FQN"""
        cq = CypherQuery('tests.cql.from_module')
        assert str(cq) == 'MATCH (n) RETURN COUNT(n)\n'

    def test_module_new_relative(self):
        """Check module import using relative notation"""
        cq = CypherQuery('.cql.from_module')
        assert str(cq) == 'MATCH (n) RETURN COUNT(n)\n'

    def test_blank_constructor_and_str_type_error(self):
        """Check we can create a blank object, and that it will raise
        a TypeError when str() is called on it."""
        cq = CypherQuery()
        try:
            str(cq)
        except TypeError:
            assert True
        else:
            assert False

    def test_blank_constructor_repr(self):
        """Check that the blank object is shown correctly in __repr__()"""
        cq = CypherQuery()
        assert repr(cq) == 'CypherQuery()'

    def test_illegal_arguments(self):
        """Check that a ValueError is raised when an illegal
        combination of argments is passed"""
        try:
            CypherQuery('tests.cql.from_module',
                        query='MATCH (n) RETURN COUNT(n)')
        except ValueError:
            assert True
        else:
            assert False

    def test_param_map_is_empty_when_blank(self):
        """When the query is None, an empty ParameterMap should be
        passed by params"""
        cq = CypherQuery()
        assert len(cq.params) == 0

class MyComplexQuery(CypherQuery):
    """Test complex query subclassing CypherQuery"""
    def __init__(self):
        self._query = 'CREATE (a:Node) SET a += {a_params}'

    def set_return_node_id(self):
        """Call this method to make the query return the ``id`` of
        ``a``"""
        self._query += '\nRETURN id(a) AS a_id'

class TestSubclassingTestCase(TestCase):
    """Test the subclassing interface"""
    def test_subclassing(self):
        """Check that complex query params work as expected"""
        cq = MyComplexQuery()
        cq.set_return_node_id()

        assert 'RETURN id(a) AS a_id' in str(cq)
        assert 'a_params' in cq.params
