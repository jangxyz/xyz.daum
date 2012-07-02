#!/usr/bin/python

import unittest
import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

from mock import Mock, MagicMock, patch, sentinel

class SomeClass:
    attribute = None

    @staticmethod
    def static_method():
        print 'called from original Class'

class ProductionClass:
    def method(self):
        pass
    def something(self, a, b, c):
        pass
    def closer(self, something):
        something.close()



class MagicMockTestCase(unittest.TestCase):
    def test_magic_mock_example(self):
        real = ProductionClass()
        real.something = MagicMock()
        real.method()
        real.something.assert_called_once_with(1, 2, 3)

class MockMethodCallsForAnObject(unittest.TestCase):
    def test_calling_method_was_called_correctly_inside(self):
        class ProductionClass:
            def closer(self, something):
                something.close()

        real = ProductionClass()
        mock = Mock()
        real.closer(mock)
        mock.close.assert_called_with()
        
class MockingClasses(unittest.TestCase):
    def test_returning_value(self):
        def some_function():
            from package import module
            instance = module.Foo()
            return instance.method()

        with patch('module.Foo') as mock:
            instance = mock.return_value
            instance.method.return_value = 'the result'
            result = some_function()
            assert result == 'the result'
        


class PatchTestCase(unittest.TestCase):
    original = SomeClass.attribute

    def tearDown(self):
        assert SomeClass.attribute == self.__class__.original

    @patch.object(SomeClass, 'attribute', sentinel.attribute)
    def test_patch_object(self):
        assert SomeClass.attribute == sentinel.attribute

    @patch('package.module.attribute', sentinel.attribute)
    def test_patch_module(self):
        from package.module import attribute
        assert attribute is sentinel.attribute

    @patch('package.module.ClassName.attribute', sentinel.attribute)
    def test_dotted_patch(self):
        ''' module name can be dotted, in the form package.module '''
        from package.module import ClassName
        assert ClassName.attribute == sentinel.attribute

    def test_patching_a_builtin(self):
        mock = MagicMock(return_value=sentinel.file_handle)
        with patch('__builtin__.open', mock):
            handle = open('filename', 'r')

        mock.assert_called_with('filename', 'r')
        assert handle == sentinel.file_handle, "incorrect file handle returned"
   

    @patch.object(SomeClass, 'static_method')
    def test_passing_mock_as_argument(self, mock_method):
        SomeClass.static_method()
        mock_method.assert_called_with()
   

    @patch('package.module.ClassName1')
    @patch('package.module.ClassName2')
    def test_stack_up_mutliple_decorators(self, MockClass2, MockClass1):
        import package
        self.assertTrue(package.module.ClassName1 is MockClass1)
        self.assertTrue(package.module.ClassName2 is MockClass2)
    
    def test_patching_dict_temporarily(self):
        foo = {'key': 'value'}
        original = foo.copy()
        with patch.dict(foo, {'newkey': 'newvalue'}, clear=True):
            assert foo == {'newkey': 'newvalue'}
        
        assert foo == original
    
    def test_patch_object_with_as(self):
        with patch.object(ProductionClass, 'method') as mock_method:
            mock_method.return_value = None
            real = ProductionClass()
            real.method(1, 2, 3)
        
        mock_method.assert_called_with(1, 2, 3)
        



if __name__ == '__main__':
    unittest.main()

