from abc import abstractproperty, ABCMeta
from functools import lru_cache
import reprlib
from six import add_metaclass

import regex

from .collections import ParameterMap, ParameterSet
from .cypher import CypherReference


class QueryComponent(object):
    # component_types
    STATEMENT = 'STATEMENT'  # i.e., a query
    STRING_LITERAL = 'STRING_LITERAL'
    MAPPING = 'MAPPING'  # either inside node or as argument
    PARAMETER_IN_BRACES = 'PARAMETER_IN_BRACES'  # e.g. {name}

    def __init__(self, components, component_type):
        self._components = [components] if isinstance(components, str) \
                                        else components
        self._component_type = component_type

    def __str__(self):
        return ''.join(str(x) for x in self.components)

    def __repr__(self):
        return 'QueryComponent({0}, component_type={1})'.format(
            repr(str(self)),
            repr(self.component_type)
        )

    def __iadd__(self, v):
        try:
            self.components[-1] += v
        except (IndexError, TypeError):
            self.components.append(v)
        return self

    def __eq__(self, other):
        try:
            if self.component_type != other.component_type \
               or str(self) != str(other):
                return False
            return True
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other

    def __len__(self):
        return len(str(self))

    def strip(self):
        return self.query_string.strip()

    @property
    def components(self):
        return self._components

    @components.setter
    def components(self, v):
        self._components = v

    @property
    def component_type(self):
        return self._component_type

    @component_type.setter
    def component_type(self, v):
        self._component_type = v


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

    @classmethod
    def parse_cypher(cls, s):
        """Parse cypher into query components
        """
        # first chunk out the string literals
        # and get rid of new lines and whitespace in non-string literals
        qc = [
            ' '.join([l.strip()
                      for l in str(x).split('\n')])
            if isinstance(x, str) else x
            for x in cls.detect_string_literals(s)
        ]

        # chunk out mappings
        qc = cls.detect_in_braces(qc)
        # listcomps

        return qc

    @staticmethod
    def split_to_statements(q):
        """Split a query into statments (i.e., seperated by semicolons)
        """
        qs = []



    @classmethod
    def detect_in_braces(cls, q):
        """Detect mappings and some params in a query

        :param q: query, represented as a list of strings and
                  QueryComponents
        """
        qs = []
        for x in q:
            if isinstance(x, QueryComponent):
                x.components = cls.detect_in_braces(x.components)
                x = [x]
            qs.extend(x)
        mapping_starter = '{'
        mapping_ender = '}'
        current_depth = 0
        output = []
        for c in qs:
            if c == mapping_starter:
                current_depth += 1
                if current_depth == 1:
                    # start a new mapping
                    output.append(
                        QueryComponent(
                            '',
                            QueryComponent.PARAMETER_IN_BRACES
                        )
                    )
            try:
                output[-1] += c
            except IndexError:
                output.append(c)
            except TypeError:
                output.append(c)
            if current_depth > 0 \
               and c == ':' \
               and output[-1].component_type == QueryComponent.PARAMETER_IN_BRACES:
                output[-1].component_type = QueryComponent.MAPPING
            if c == mapping_ender:
                current_depth -= 1
                if current_depth == 0:
                    output.append('')


        return output



    @staticmethod
    def detect_string_literals(s):
        output = []
        current_delimiter = None
        delimeters = ['"', "'"]  # quote marks
        escape_chars = '\\'
        for i, c in enumerate(s):
            # if no delimiter currently, find one
            if current_delimiter is None and c in delimeters:
                # found it!
                current_delimiter = c
                # start a new string literal
                output.append(QueryComponent(c, 'STRING_LITERAL'))
            elif c == current_delimiter \
                 and s[i - 1 if i >= 1 else 0] not in escape_chars:
                # end the string literal
                try:
                    output[-1] += c
                except IndexError:
                    output.append(c)
                current_delimiter = None
                if i != len(s) - 1:
                    output.append('')
            else:
                try:
                    output[-1] += c
                except IndexError:
                    output.append(c)

        return output
