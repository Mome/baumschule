import sys, os, unittest
sys.path.insert(1, os.path.abspath('..'))


from hypara.containers import Intervall, Product, Call


class TestProduct(unittest.TestCase):
    def setUp(self):
        self.test_values = (
            ('bla', 2),
            {'foo':1, 'nee':'raa'},
        )

    def test_viewers(self):
        a,b = self.test_values
        p = Product(a, b)

        self.assertEqual(p.args, list(a))
        self.assertEqual(p.kwargs, dict(b))

        for x in (*a, *b.values()):
            self.assertIn(x, p)


class TestIntervall(unittest.TestCase):
    def setUp(self):
        pass


class TestCall(unittest.TestCase):
    def setUp(self):
        pass


if __name__ == '__main__':
    unittest    .main()
