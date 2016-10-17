from Space import Space, SpaceInferenceError
import unittest


class TestProduct(unittest.TestCase):
    def setUp(self):
        pass

    def test_exceptions(self):
        self.assertRaises(SpaceInferenceError, Space)

    def test_domain(self):
        self.assertEqual(Space(int).domain, Intervall(-float('inf'),float('inf')))
        self.assertEqual(Space(float).domain, Intervall(-float('inf'),float('inf')))
        self.assertEqual(Space(['a',1]).domain, ['a',1])

    def test_type(self):
        self.assertEqual(Space([1,2,3]).type_, 'discrete')
        self.assertEqual(Space(['a',2,3]).type_, 'categorical')
        self.assertEqual(Space(float).type_, 'continuous')
        self.assertEqual(Space(int).type_, 'discrete')
        self.assertEqual(Space('probability').type_, 'continuous')
        

class TestIntervall(unittest.TestCase):
    def setUp(self):
        pass


class TestCall(unittest.TestCase):
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest.main()
