from abc import abstractproperty, ABCMeta
import re
import reprlib
from six import add_metaclass


class AbstractCypherQuery(ABCMeta):
    """Abstract class to ensure that future query objects implement the
    rqwuired interface. This way Query objects do not need to inherit
    from CypherQuery
    """

    PARAM_FINDING_REGEX = re.compile(r'')

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
    def parames(self):
        try:
            return self._params
        except AttributeError:
            self._params = self.construct_params(self._query)

        return self._params

    @staticmethod
    def construct_params(query):
        pass
