from parameter import *
from scipy import 

class ParameterTest(unittest.TestCase):
	def setUp(self):
		pass

	def test_exceptions(self):
		self.assertRaises(Parameter, ArgumentInferenceError)
		self.assertRaises(ValueError, Parameter, [], infere_prior=0)

	def test_infer_domain(self):
		infdom = Parameter.infer_domain
		self.assertEuqal(infdom, ArgumentInferenceError, (None,None,None))
		self.assertEqual(infdom, ArgumentInferenceError, (None,None,None))

	def test_infere_type(self):
		...

if __name__ == '__main__':
    unittest.main()
