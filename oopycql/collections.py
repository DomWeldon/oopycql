try:
    from collections import UserDict
except ImportError:
    # python2
    class UserDict(object):
        def __init__(self):
            self.data = {}

from .errors import ParameterNotSetError


class ParameterMap(UserDict):
    def __init__(self, keys=None):
        """Initialize from a ParameterSet to create an empty mapping of
        parameters.

        :param keys: iterable of parameter names
        """
        UserDict.__init__(self)
        self._keys = keys

    def keys(self):
        return self._keys

    def items(self):
        return [(k, self[k]) for k in self.keys()]

    def iteritems(self):
        return self.items()

    def __repr__(self):
        return 'ParameterMap({0})'.format(repr({k for k in self.keys()}))

    def __str__(self):
        return repr(self)

    def __setitem__(self, k, v):
        if k not in self.keys():
            raise ParameterNotSetError((
                'Parameters can only be set if they are already specified '
                'in the cypher query.'
            ))
        self.data[k] = v

    def __getitem__(self, k):
        try:
            return self.data[k]
        except KeyError:
            if k in self.keys():
                return None

        raise ParameterNotSetError((
            'The parameter you specified was not found in your query.'
        ))

    def __iter__(self):
        return self.keys()

    def __len__(self):
        return len(self.keys())

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for k, v in self.items():
            if other[k] != v:
                return False

        return True

    def __ne__(self, other):
        return not(self.__eq__(other))

    def __bool__(self):
        return len(self) > 0


class ParameterSet(set):
    pass
