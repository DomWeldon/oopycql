from abc import abstractproperty, ABCMeta
try:
    from functools import lru_cache
except ImportError:  # pragma: no cover
    from functools32 import lru_cache  # pragma: no cover
import inspect
from six import add_metaclass
from pathlib import Path
from pprint import pprint

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
        pass  # pragma: no cover


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

    @classmethod
    @lru_cache(maxsize=64)
    def from_file(cls, filename, relative_to=None):
        """Exactly like `load_from_file`, but cached.
        """
        return cls.load_from_file(filename, relative_to=relative_to,
                                  depth=2)

    @classmethod
    def load_from_file(cls, filename, relative_to=None, depth=1):
        """Constructor to load a CypherQuery object from a file.

        :param filename: either a ``Path`` object or a string filename
        :param relative_to: directory relative to which the query
                            should be found, either a string or Path
                            object; if left as None, then will be
                            called relative to the file which called
                            the function (i.e., previous file in
                            the stack)
        :return: CypherQuery
        """
        f = filename if isinstance(filename, Path) else Path(filename)
        if relative_to is None:
            relative_to = Path(inspect.stack()[depth].filename).parent
        elif not isinstance(relative_to, Path):
            relative_to = Path(relative_to)
        f = relative_to / f
        with f.open('r') as _:
            q = _.read()
        return cls(q)
