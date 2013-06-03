#!/usr/bin/env python2
import unittest

from robotsparser import RobotsTXTParser

class TestRobots(unittest.TestCase):
    def setUp(self):
        pass
        
    def test_empty(self):
        rp = RobotsTXTParser("")
        rp.path_acceptable("/")

if __name__=="__main__":
    unittest.main()
