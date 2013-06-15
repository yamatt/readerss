#!/usr/bin/env python2
import sys
from datetime import timedelta
from models.interface import Interface
import settings
from models.model import Feed, Entry
from helpers import seconds_to_upper_minutes

db = Interface(settings.DATABASE_ENGINE, settings.DATABASE_CONNECTION_STRING)

if __name__ == "__main__":
    for feed in db.get_all_feeds():
        print u"Feed: {0}".format(feed.title)
        entries = db.connection.get_items(Entry.TYPE, feed_id=feed.id)
        if len(entries):
            for entry in entries:
                entry = db.get_entry(entry['id'])   # cheating here should really convert to Entry object but meh
                print u" - {0}".format(entry.title)
        else:
            print u"   No entries found"
            
    all_feed = db.connection.get_items(Feed.TYPE)
    all_entries = db.connection.get_items(Entry.TYPE)
    print "There were {0} feeds and {1} entries".format(len(all_feed), len(all_entries))
    
