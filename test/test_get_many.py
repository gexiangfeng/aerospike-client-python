# -*- coding: utf-8 -*-

import pytest
import sys
from test_base_class import TestBaseClass

try:
    import aerospike
except:
    print "Please install aerospike python client."
    sys.exit(1)

class TestGetMany(TestBaseClass):
    def setup_class(cls):
        """
        Setup method.
        """
        hostlist, user, password = TestBaseClass.get_hosts()
        config = {
                'hosts': hostlist
                }
        if user == None and password == None:
            TestGetMany.client = aerospike.client(config).connect()
        else:
            TestGetMany.client = aerospike.client(config).connect(user, password)

    def teardown_class(cls):
        TestGetMany.client.close()

    def setup_method(self, method):
        self.keys = []

        for i in xrange(5):
            key = ('test', 'demo', i)
            rec = {
                    'name' : 'name%s' % (str(i)),
                    'age'  : i
                    }
            TestGetMany.client.put(key, rec)
            self.keys.append(key)


    def teardown_method(self, method):

        """
        Teardown method.
        """
        for i in xrange(5):
            key = ('test', 'demo', i)
            TestGetMany.client.remove(key)

    def test_get_many_without_any_parameter(self):

        with pytest.raises(TypeError) as typeError:
            TestGetMany.client.get_many()

        assert "Required argument 'keys' (pos 1) not found" in typeError.value

    def test_get_many_without_policy(self):

        records = TestGetMany.client.get_many( self.keys )

        assert type(records) == dict
        assert len(records.keys()) == 5

    def test_get_many_with_proper_parameters(self):

        records = TestGetMany.client.get_many( self.keys, { 'timeout': 3 } )

        assert type(records) == dict
        assert len(records.keys()) == 5
        assert records.keys() == [0, 1, 2, 3, 4]

    def test_get_many_with_none_policy(self):

        records = TestGetMany.client.get_many( self.keys, None )

        assert type(records) == dict
        assert len(records.keys()) == 5
        assert records.keys() == [0, 1, 2, 3, 4]

    def test_get_many_with_none_keys(self):

        with pytest.raises(Exception) as exception:
            TestGetMany.client.get_many( None, {} )

        assert exception.value[0] == -1
        assert exception.value[1] == "Keys should be specified as a list or tuple."

    def test_get_many_with_non_existent_keys(self):

        self.keys.append( ('test', 'demo', 'non-existent') )

        records = TestGetMany.client.get_many( self.keys )

        assert type(records) == dict
        assert len(records.keys()) == 5
        assert records.keys() == [0, 1, 2, 3, 4]

    def test_get_many_with_all_non_existent_keys(self):

        keys = [( 'test', 'demo', 'key' )]

        records = TestGetMany.client.get_many( keys )

        assert len(records.keys()) == 0
        assert records == {}

    def test_get_many_with_invalid_key(self):

        with pytest.raises(Exception) as exception:
            records = TestGetMany.client.get_many( "key" )

        assert exception.value[0] == -1
        assert exception.value[1] == "Keys should be specified as a list or tuple."

    def test_get_many_with_invalid_timeout(self):

        policies = { 'timeout' : 0.2 }
        with pytest.raises(Exception) as exception:
            records = TestGetMany.client.get_many(self.keys, policies)

        assert exception.value[0] == -2
        assert exception.value[1] == "timeout is invalid"

    def test_get_many_with_non_existent_keys_in_middle(self):

        self.keys.append( ('test', 'demo', 'non-existent') )

        for i in xrange(15,20):
            key = ('test', 'demo', i)
            rec = {
                    'name' : 'name%s' % (str(i)),
                    'age'  : i
                    }
            TestGetMany.client.put(key, rec)
            self.keys.append(key)

        records = TestGetMany.client.get_many( self.keys )

        for i in xrange(15,20):
            key = ('test', 'demo', i)
            TestGetMany.client.remove(key)

        assert type(records) == dict
        assert len(records.keys()) == 10
        assert records.keys() == [0, 1, 2, 3, 4, 15, 16, 17, 18, 19]