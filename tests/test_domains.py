
import unittest
from math import inf

from treefarm.core.domains import ParameterList, Intervall, R, N, Z

class TestParameterList(unittest.TestCase):
    def setUp(self):
        pass


class TestIntervall(unittest.TestCase):
    def setUp(self):
        self.A = Intervall(-12.6, 18.5, 0.1, False, True)
        self.B = Intervall(-12.6, 18.5, 0.1, True, False)
        self.C = Intervall(-123.65, 122.79, 11.11, False, True)

    def test_other(self):
        self.assertTrue(N.closed)
        self.assertFalse(R.closed)
        self.assertTrue(self.A.bounded)
        self.assertFalse(N.bounded)

    def test_contains(self):
        for i in [0, 1, -100, 111.111, -.5]:
            self.assertIn(i, R)
        for i in [inf, -inf]:
            self.assertNotIn(i, R)

        for i in [1, 100, 3, 5]:
            self.assertIn(i, N)
        for i in [inf, -inf, .01, 0, -1, -.3]:
            self.assertNotIn(i, N)

        for i in [18.5, 0, 1.1, -1.1]:
            self.assertIn(i, self.A)
        for i in [inf, -inf, -12.6, 0.11, -0.23]:
            self.assertNotIn(i, self.A)

        for i in [-12.6, 0, 1.1, -1.1]:
            self.assertIn(i, self.B)
        for i in [18.5, 0.11, -0.23]:
            self.assertNotIn(i, self.B)

        for i in [-112.54]:
            self.assertIn(i, self.C, )
        for i in [-123.65, 122.79]:
            self.assertNotIn(i, self.C)

    def test_getitem(self):
        ...

    def test_iter(self):
        ...

    def test_str(self):
        ...


if __name__ == '__main__':
    unittest.main()
