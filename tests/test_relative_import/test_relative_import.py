from unittest import TestCase

from oopycql.query import CypherQuery


class RelativeImportTestCase(TestCase):
    """Slightly oddly placed test to check that the relative import
    feature, when importing from a sibling (or more distant) directory
    behaves as expected.
    """
    def test_relative_import(self):
        cq = CypherQuery('..cql.from_module')
        assert str(cq) == 'MATCH (n) RETURN COUNT(n)\n'
