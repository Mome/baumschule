# -*- coding: utf-8 -*-
"""
Created on Mon May 23 19:02:05 2016

@author: mome
"""

import unittest
from parameter import Parameter
from itertools import islice

class TestParameter(unittest.TestCase):
    
    def setUp(self):
        self.iterations = 100
    
    def test_discrete(self):
        start, end = -10, 10
        para = Parameter(
            type_='discrete',
            range_=range(start, end+1))
        for value in islice(iter(para), self.iterations):
            unittest.assertIn(value, range(start, end+1))
    
    def test_categorical(self):
        cat = tuple("ABCDEFGHIJKLMNO")
        para = Parameter(values=cat)
        unittest.assertEqual(para.type_, 'categorical')
        for value in islice(iter(para), self.iterations):
            unittest.assertIn(value, cat)
            
    def test_continuous(self):
        start, end = -10, 10
        para = Parameter(
            type_='continuous',
            range_=[start, end])
        for value in islice(iter(para), self.iterations):
            unittest.assertTrue(start <= value < end)
        
if __name__ == "__main__":
    unittest.main()