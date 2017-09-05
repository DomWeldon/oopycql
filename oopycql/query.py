from pprint import pprint
from abc import abstractproperty, ABCMeta
try:
    from functools import lru_cache
except ImportError:  # pragma: no cover
    from functools32 import lru_cache  # pragma: no cover
import inspect
try:
    reduce
except NameError:
    # python3
    from functools import reduce
from six import add_metaclass
from pathlib import Path

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
    def __new__(cls, *args, **kwargs):
        """Constructor, optionally passing query as a string.

        :param query: cypher query as string
        :param fqn: Fully Qualified Name to import the query as
        """
        try:
            query = kwargs['query']
        except KeyError:
            query = None

        if len(args) == 1 and query is None:
            fqn = args[0]
            if fqn[0] == '.':
                relative_to = None
                fqn = fqn[1:]
            else:
                relative_to = './'
            filename = reduce(lambda x, y:  x / Path(y), fqn.split('.'))
            try:
                unicode
            except NameError:
                depth = 3
                pass
            else:
                depth = 4
            return cls.from_file(filename.with_suffix('.cql'),
                                 relative_to=relative_to,
                                 depth=depth)
        elif len(args) == 0 and query is not None:
            cq = object.__new__(cls)
            cq._query = query
            return cq

        elif len(args) == 0 and query is None:
            return object.__new__(cls)

        raise ValueError('Illegal argument combination')

    def __init__(self, *arks, **kwargs):
        pass

    def __str__(self):
        """Return the query for use in graph."""
        try:
            return self._query
        except AttributeError:
            raise TypeError

    def __repr__(self):
        try:
            if len(self._query) >= 40:
                end = 37
                dots = '...'
            else:
                end = 40
                dots = ''

            return 'CypherQuery("{0}")'.format(self._query[:end] + dots)
        except (AttributeError, TypeError):
            return 'CypherQuery()'

    @classmethod
    def from_module(cls, f, extension='.cql'):
        """Load a CQL query from the current module. By default, it is
        assumed that there is directory called CQL which contains the
        queries.

        :param f: filename of the query
        :param submodule: the directory name to load from, cql by
                          default, if None then will use current module
                          directory.
        :param extension: the file extension (inc dot) of the query, if
                          None then will assume no extension
        :rtype: CypherQuery
        :return: CypherQuery
        """
        p = Path(f)
        if extension is not None:
            p = p.with_suffix(extension)
        try:
            unicode
        except NameError:
            # python3
            depth = 3
            pass
        else:
            # python2
            depth = 4
        return cls.from_file(p, depth=depth)

    @classmethod
    @lru_cache(maxsize=64)
    def find_params_in_query(cls, query):
        params = cls.PARAM_FINDING_REGEX.findall(query)

        def one_or_other(*args):
            return [a for a in args if len(a) > 0][0]

        return ParameterSet([one_or_other(*p) for p in params])

    @classmethod
    @lru_cache(maxsize=64)
    def from_file(cls, filename, relative_to=None, depth=2):
        """Exactly like `load_from_file`, but cached using
        ``functools.lru_cache`` (or the python 2 equivalent using
        ``functools32``) to prevent constantly reading files to load
        the same queries. ``maxsize`` is set at 64.
        """
        return cls.load_from_file(filename, relative_to=relative_to,
                                  depth=depth)

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
        :param depth: when relative_to is None, the function will
                      use inspect.stack() to find the file in which
                      the function was called. depth is the integer
                      index of the stack where this file is found,
                      if this function is called from another function
                      (e.g., the cahced method above), then the depth
                      needs to be increased.
        :return: CypherQuery
        """
        f = filename if isinstance(filename, Path) else Path(filename)
        if relative_to is None:
            try:
                relative_to = Path(inspect.stack()[depth].filename).parent
            except AttributeError:
                # python 2.7 issue
                if 'functools' in inspect.stack()[depth][1]:
                    depth += 1
                pprint(inspect.stack()[depth-1:depth+2])
                relative_to = Path(inspect.stack()[depth][1]).parent
        elif not isinstance(relative_to, Path):
            relative_to = Path(relative_to)
        f = relative_to / f
        with f.open('r') as _:
            q = _.read()
        cq = object.__new__(cls)
        cq._query = q
        return cq

    @property
    def params(self):
        """A ParameterMap of all the parameters in the query alongside
        their values, if assigned. If no value is assigned to a param
        yet, None is assumed.
        """
        try:
            return self._params
        except AttributeError:
            self._params = ParameterMap(
                self.find_params_in_query(self._query)
            )

        return self._params
