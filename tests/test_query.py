from collections import namedtuple
from pprint import pprint
from unittest import TestCase

from oopycql.query import CypherQuery, QueryComponent


class RegexForParameterFindingTestCase(TestCase):
    TestParamFinderQuery = namedtuple('TestParamFinderQuery', 'query params')
    TEST_QUERIES = [
        TestParamFinderQuery(
			'MATCH (a:Node) WHERE a.name = {param} AND a.woof = {param2}',
			{'param', 'param2'}
		),
		TestParamFinderQuery(
			'MATCH (a:Node) WHERE a.name = $param',
			{'param'}
		),
		TestParamFinderQuery(
			'MATCH (a:Node { name: { param } })',
			{'param'}
		),
		TestParamFinderQuery(
			'MATCH (a:Node { name: $param })',
			{'param'}
		),
		TestParamFinderQuery(
			'MATCH (a:Node { name: $héllo })',
			{'héllo'}
		),
		TestParamFinderQuery(
			'MATCH (a) WHERE a.p = { a¢1轉123 } RETURN *',
			{'a¢1轉123'}
		),
        TestParamFinderQuery(
			'MATCH (a) WHERE a.p = { a¢1轉123 } '
            + 'AND a.q <> { a¢1轉123 } RETURN *',
			{'a¢1轉123'}
		),
        TestParamFinderQuery(
			'MATCH (a) WHERE a.p = { a¢1轉123 } '
            + 'AND a.q <> $a¢1轉123 RETURN *',
			{'a¢1轉123'}
		),
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


class DetectStringLiteralsTestCase(TestCase):
    StringLiteralDetectionTestQuery = namedtuple(
        'StringLiteralDetectionTestQuery',
        'query ordered_string_literals'
    )
    CYPHER_TEST_QUERIES = [
        StringLiteralDetectionTestQuery(
            """MATCH (start:Node)-[:REL]->(a)-[:REL]->(b)
               WITH
                 collect(distinct a) as aNodes,
                 collect(distinct b) as bNodes
               CALL apoc.when(size(aNodes) <= size(bNodes),
                              'RETURN aNodes as resultNodes',
                              'RETURN bNodes as resultNodes',
                              {aNodes:aNodes, bNodes:bNodes}) YIELD value
               RETURN value.resultNodes as resultNodes""",
            [
                "'RETURN aNodes as resultNodes'",
                "'RETURN bNodes as resultNodes'",
            ]),
        StringLiteralDetectionTestQuery(
            """MATCH (me:User{id:{myId}})
               CALL apoc.case(
                [{selection} = 'friends',
                 "RETURN [(me)-[:FRIENDS]-(friend) | friend] as selection",
                 {selection} = 'coworkers',
                 "RETURN [(me)-[:WORKS_AT*2]-(coworker) | coworker] as selection",
                 {selection} = 'all',
                 "RETURN apoc.coll.union(
                    [(me)-[:FRIENDS]-(friend) | friend],
                    [(me)-[:WORKS_AT*2]-(coworker) | coworker]) as selection"
                ],
                'RETURN [] as selection',
                {me:me}) YIELD value
               RETURN value.selection as selection""",
            [
                "'friends'",
                '"RETURN [(me)-[:FRIENDS]-(friend) | friend] as selection"',
                "'coworkers'",
                '"RETURN [(me)-[:WORKS_AT*2]-(coworker) | coworker] as selection"',
                "'all'",
                '''"RETURN apoc.coll.union(
                    [(me)-[:FRIENDS]-(friend) | friend],
                    [(me)-[:WORKS_AT*2]-(coworker) | coworker]) as selection"''',
                "'RETURN [] as selection'",
            ])
    ]
    def test_returns_list(self):
        s = 'hello world'
        assert CypherQuery.detect_string_literals(s) == [s]

    def test_detects_string_literal(self):
        s = 'hello "world"'
        assert CypherQuery.detect_string_literals(s) == [
            'hello ',
            QueryComponent('"world"', QueryComponent.STRING_LITERAL),
        ]

    def test_detects_nested_string_literal(self):
        s = 'Pat said "I read \\"The Times\\"" to Sidney.'
        r = CypherQuery.detect_string_literals(s)
        print(r)
        assert r == [
            'Pat said ',
            QueryComponent('"I read \\"The Times\\""',
                           QueryComponent.STRING_LITERAL),
            ' to Sidney.',
        ]

    def test_with_cypher_examples(self):
        for tq in self.CYPHER_TEST_QUERIES:
            r = CypherQuery.detect_string_literals(tq.query)
            assert sum([len(x) for x in r]) == len(tq.query)
            pprint([(type(x), repr(x)) for x in r])
            literals = [x for x in r if isinstance(x, QueryComponent)]
            for i, sl in enumerate(literals):
                assert sl == QueryComponent(tq.ordered_string_literals[i],
                                            QueryComponent.STRING_LITERAL)
