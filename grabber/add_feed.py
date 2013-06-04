#!/usr/bin/env python2
import sys
from datetime import timedelta
from models.interface import Interface
import settings
from models.model import Feed
from robotsparser import RobotsTXTParser
from helpers import seconds_to_upper_minutes

db = Interface(settings.DATABASE_ENGINE, settings.DB_CONNECTION_STRING)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        robotstxt = RobotsTXTParser.from_url(url)
        if robotstxt.url_acceptable(url):
            #try:
                new_feed = Feed.from_url(url)
                current_delay = timedelta(minutes=new_feed.minimum_wait)
                robots_delay = robotstxt.get_crawl_delay()
                
                if robots_delay and robots_delay > current_delay:
                    new_feed.minimum_wait = seconds_to_upper_minutes(robots_delay)
                db.add_feed(new_feed)
            #except AttributeError as e:
            #    raise RuntimeError("Specified URL could not be read. Not a RSS/Atom feed? Error: {0}".format(e))
        else:
            raise RuntimeError("URL specified cannot be accessed because of robots.txt")
    else:
        raise RuntimeError("Need url as first argument")
