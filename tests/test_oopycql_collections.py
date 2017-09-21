from unittest import TestCase

from oopycql.errors import ParameterNotSetError
from oopycql.oopycql_collections import ParameterMap, ParameterSet


class ParameterSetTestCase(TestCase):
    """This is just a subclass of ``set``, so nothing to test yet"""
    pass


class ParameterMapTestCase(TestCase):
    """A dictionary like collection used to store parameters in a CQL
    query, and to set their values."""
    def get_param_map(self):
        """handy little constructor for use in tests"""
        pm = ParameterMap(ParameterSet(('param1', 'param2')))
        return pm

    def test_repr_is_true_constructor_and_equality(self):
        """Check repr method returns a true constructor, like dict
        """
        pm = self.get_param_map()
        print(pm, eval(repr(pm)))
        assert eval(repr(pm)) == pm

    def test_will_iter_keys(self):
        """Check keys can be iterated on"""
        pm = self.get_param_map()
        keys = [k for k in pm]
        assert len(keys) == 2
        for k in pm.keys():
            assert k in keys

    def test_str_is_repr(self):
        """Check str() returns same as repr() like dict"""
        pm = self.get_param_map()
        assert str(pm) == repr(pm)

    def test_python2_iteration(self):
        """Check python2 style iteration is supported"""
        pm = self.get_param_map()
        try:
            d = {k: v for k, v in pm.iteritems()}
            for k in pm.keys():
                assert k in d
                assert d[k] == pm[k]
        except Exception:
            assert False
        else:
            assert True

    def test_iteration_on_items(self):
        """Check items() method is iterable"""
        pm = self.get_param_map()
        print(pm)
        try:
            d = {k: v for k, v in pm.items()}
            for k in pm.keys():
                assert k in d
                assert d[k] == pm[k]
        except Exception:
            assert False
        else:
            assert True

    def test_equality_and_inequality_on_value(self):
        """Check equality and inequality when values are the
        same or different"""
        pm = self.get_param_map()
        pm2 = self.get_param_map()
        assert pm == pm2
        pm2['param1'] = 2
        assert pm != pm2
        pm['param1'] = 2
        assert pm == pm2

    def test_inequality_on_length(self):
        """Check for inequality when lengths are different"""
        pm = self.get_param_map()
        pm2 = ParameterMap()
        assert pm != pm2

    def test_len_and_bool(self):
        """len() and bool() interfaces"""
        pm = self.get_param_map()
        assert len(pm) == 2
        assert bool(pm) is True
        pm = ParameterMap({})
        assert bool(pm) is False

    def test_set_get_attr(self):
        """Check set and get attr"""
        pm = self.get_param_map()
        try:
            pm['param1'] = 1
            pm['param2'] = 2
            assert pm['param1'] == 1, pm['param2'] == 2
        except:
            assert False

    def test_attr_not_found_on_set(self):
        """Check for custom exception on param not set"""
        pm = self.get_param_map()
        try:
            pm['param3'] = 3
        except ParameterNotSetError:
            assert True
        else:
            assert False

    def test_attr_not_found_on_set_with_key_error(self):
        """Check KeyError works as a catch"""
        pm = self.get_param_map()
        try:
            pm['param3'] = 3
        except KeyError:
            assert True
        else:
            assert False

    def test_attr_not_found_on_get(self):
        """Check for custom exception on param get
        """
        pm = self.get_param_map()
        try:
            pm['param3']
        except ParameterNotSetError:
            assert True
        else:
            assert False

    def test_attr_not_found_on_get_key_error(self):
        """Check for custom exception on param get
        """
        pm = self.get_param_map()
        try:
            pm['param3']
        except KeyError:
            assert True
        else:
            assert False
