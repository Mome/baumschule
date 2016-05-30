from parameter import *
import unittest

class ParameterTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_exceptions(self):
        self.assertRaises(ArgumentInferenceError, Parameter)
        self.assertRaises(ValueError, Parameter, [], infere_prior=2)
        self.assertRaises(ArgumentInferenceError, Parameter, type_='cat')

    def test_domain(self):
        self.assertEqual(Parameter(int).domain, Intervall(-float('inf'),float('inf')))
        self.assertEqual(Parameter(float).domain, Intervall(-float('inf'),float('inf')))
        self.assertEqual(Parameter(['a',1]).domain, ['a',1])

    def test_type(self):
        ...
        

if __name__ == '__main__':
    unittest.main()
