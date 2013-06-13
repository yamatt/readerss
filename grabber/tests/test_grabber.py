#!/usr/bin/env python2
import unittest
from tests.mocks import Feed
from mockito import *
from grabber import FeedGrab

class TestFeedGrab(unittest.TestCase):
    def setUp(self):
        self.feed_queue = mock()
        self.database_queue = mock()
        self.exit_set = mock()
        
        self.feedgrab = FeedGrab(self.feed_queue, self.database_queue, self.exit_set)
        
    def test_get_latest(self):
        self.feedgrab.get_latest(Feed)

if __name__=="__main__":
    unittest.main()
