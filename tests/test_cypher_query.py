from unittest import TestCase

from oopycql.query import CypherQuery


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
