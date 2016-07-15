from parameter import Parameter, ArgumentInferenceError
import unittest

class TestParameter(unittest.TestCase):
    def setUp(self):
        pass

    def test_exceptions(self):
        self.assertRaises(ArgumentInferenceError, Parameter)
        self.assertRaises(ValueError, Parameter, [], infere_prior=2)
        self.assertRaises(ArgumentInferenceError, Parameter, type_='cat')
        self.assertRaises(ArgumentInferenceError, Parameter, domain=object() )
        self.assertRaises(ArgumentInferenceError, Parameter, 'real')
        self.assertRaises(ArgumentInferenceError, Parameter, 'positiv')
        self.assertRaises(ArgumentInferenceError, Parameter, 'negativ')

    def test_domain(self):
        self.assertEqual(Parameter(int).domain, Intervall(-float('inf'),float('inf')))
        self.assertEqual(Parameter(float).domain, Intervall(-float('inf'),float('inf')))
        self.assertEqual(Parameter(['a',1]).domain, ['a',1])

    def test_type(self):
        self.assertEqual(Parameter([1,2,3]).type_, 'discrete')
        self.assertEqual(Parameter(['a',2,3]).type_, 'categorical')
        self.assertEqual(Parameter(float).type_, 'continuous')
        self.assertEqual(Parameter(int).type_, 'discrete')
        self.assertEqual(Parameter('probability').type_, 'continuous')
        

if __name__ == '__main__':
    unittest.main()
