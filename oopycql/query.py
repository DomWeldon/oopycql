from abc import abstractproperty, ABCMeta
try:
    from functools import lru_cache
except ImportError:
    from functools32 import lru_cache
from six import add_metaclass

import regex

from .oopycql_collections import ParameterMap, ParameterSet
from .cypher import CypherReference


class AbstractCypherQuery(ABCMeta):
    """Abstract class to ensure that future query objects implement the
    rqwuired interface. This way Query objects do not need to inherit
    from CypherQuery
    """

    PARAM_FINDING_REGEX = regex.compile(CypherReference.PARAM_FINDING_REGEX)
    """Find a cypher parameter in a query."""

    @property
    @abstractproperty
    def params(self):
        pass


@add_metaclass(AbstractCypherQuery)
class CypherQuery(object):
    """Interface for a cypher query.
    """
    def __init__(self, query=None):
        """Construct, optionally passing query as a string.

        :param query: cypher query as string
        """
        self._query = query

    def __str__(self):
        """Return the query for use in graph."""
        return self._query

    def __repr__(self):
        if len(self._query) >= 40:
            end = 37
            dots = '...'
        else:
            end = 40
            dots = ''

        return '<CypherQuery ("{0}")>'.format(self._query[:end] + dots)

    @property
    def params(self):
        try:
            return self._params
        except AttributeError:
            self._params = ParameterMap(
                self.find_params_in_query(self._query)
            )

        return self._params

    @classmethod
    @lru_cache(maxsize=64)
    def find_params_in_query(cls, query):
        params = cls.PARAM_FINDING_REGEX.findall(query)

        def one_or_other(*args):
            return [a for a in args if len(a) > 0][0]

        return ParameterSet([one_or_other(*p) for p in params])
