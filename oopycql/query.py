from abc import abstractproperty, ABCMeta
import reprlib
from six import add_metaclass

import regex

from .collections import ParameterMap, ParameterSet


class AbstractCypherQuery(ABCMeta):
    """Abstract class to ensure that future query objects implement the
    rqwuired interface. This way Query objects do not need to inherit
    from CypherQuery
    """

    PARAM_FINDING_REGEX = regex.compile((
        '{ *([^\p{Sc}\p{S}][^\p{Sm}\p{So}\p{Sk}\p{C}\p{Z}\p{P}\p{M}]+) *}'
        '|\$([^\p{Sc}\p{S}][^\p{Sm}\p{So}\p{Sk}\p{C}\p{Z}\p{P}\p{M}]+)'))
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
    def find_params_in_query(cls, query):
        params = cls.PARAM_FINDING_REGEX.findall(query)
        one_or_other = lambda x, y: x if len(y) == 0 else y
        return ParameterSet([one_or_other(*p) for p in params])
