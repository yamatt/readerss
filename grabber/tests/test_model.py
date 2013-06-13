#!/usr/bin/env python2
import unittest
from datetime import datetime, timedelta

from models.model import Feed

class TestFeed(unittest.TestCase):
    def setUp(self):
        self.feed=Feed(
        id = "random id",
        url = "http://www.example.com/feed.rss",
        title = "Example Feed",
        subtitle = "Used for testing feed entries",
        updated = datetime.now(),
        published = datetime.now(),
        link = "http://www.example.com/feeds",
        last_accessed = datetime.now(),
        minimum_wait = 3,
        errors = 0,
    )
        
    def test_can_check(self):
        # not checked before
        self.feed.last_accessed = None
        self.assertTrue(self.feed.can_check())
        
        # check too recent
        now = datetime.now()
        recent_minutes = timedelta(minutes=self.feed.minimum_wait - 1) # within minimum wait time
        last_accessed = now - recent_minutes
        
        self.feed.last_accessed = last_accessed
        self.assertFalse(self.feed.can_check())
        
        # check long enough ago   
        now = datetime.now()
        recent_minutes = timedelta(minutes=self.feed.minimum_wait + 1) # outside minimum wait time
        last_accessed = now - recent_minutes
        
        self.feed.last_accessed = last_accessed
        self.assertTrue(self.feed.can_check())
        

if __name__=="__main__":
    unittest.main()
