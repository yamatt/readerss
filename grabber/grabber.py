#!/usr/bin/env python2
 
import threading
from threading import Event
from Queue import Queue, Full

from robotsparser import RobotsTXTParser

from models import Feed
from models.interface import Interface

import settings

def seconds_to_upper_minutes(s):
    """
    Takes a number of seconds and converts it to the number of minutes
    required to contain that number of seconds.
    """
    minutes = s / 60
    return s if not s % 60 else s + 1

class FeedGrab(threading.Thread):
    """
    Processes feeds to grab new entries from them.
    """
    def __init__(self, feed_queue, database_queue, stop_flag):
        """
        Sets up the thread.
        TODO: check these threading items need to be passed in here or
        in run.
        :param feed_queue:
        :param database_queue:
        :param stop_flag:
        """
        super(FeedGrab, self).__init__()
        self.feed_queue = feed_queue
        self.database_queue = database_queue
        self.stop_flag = stop_flag
        
    def run(self):
        """
        The processing that grabs new feed entries. It will determine if
        it needs to update first. Check it is allowed to update from the
        site's robots.txt and then pulls in the new feed and entries.
        """
        max_wait=timedelta(minutes=settings.MAX_ACCESS_WAIT)
        min_wait=timedelta(minutes=settings.MIN_ACCESS_WAIT)
        while not self.stop_flag.is_set():
            feed = self.feed_queue.get()
            if feed:
                try:
                    # worth checking yet?
                    if feed.last_accessed:
                        now = datetime.now()
                        # determine next access from minimum wait time
                        requested_delay = timedelta(minutes=feed.minimum_wait)
                        requested_next_access = requested_delay + feed.last_accessed
                        if now > requested_next_access:
                            robotstxt = RobotsTXTParser.from_url(url)
                            # determine next access from sites robots.txt
                            robots_delay = timedelta(seconds=robotstxt.get_crawl_delay())
                            robots_next_access = robots_delay + feed.last_accessed
                            if now > robots_next_access:
                                # check url is accessible
                                if robotstxt.url_acceptable(feed.url):
                                    new_feed = Feed.from_url(feed.url)
                                    new_feed.last_accessed = now
                                    new_feed.errors = feed.errors
                                    # determine minimum wait
                                    if robots_delay > requested_delay:
                                        # increase minimum wait to robots delay to the nearest minute up to the max wait
                                        if robots_delay > max_wait:
                                            new_feed.minimum_wait = settings.MAX_ACCESS_WAIT
                                        else:
                                            robots_minutes = seconds_to_upper_minutes(robots_delay)
                                            if robots_minutes > settings.MIN_ACCESS_WAIT:
                                                new_feed.minimum_wait = robots_minutes
                                            else:
                                                new_feed.minimum_wait = settings.MIN_ACCESS_WAIT
                                    elif robots_delay < requested_delay:
                                        # decrease the minimum wait to robots delay to the nearest upper minute down to the minimum wait
                                        if robots_delay > min_wait:
                                            new_feed.minimum_wait = seconds_to_upper_minutes(robots_delay)
                                        else:
                                            new_feed.minimum_wait = settings.MIN_ACCESS_WAIT
                                       
                                    # write feed
                                    new_feed_message = DatabaseWriterMessage(DatabaseWriterMessage.FEED, new_feed)
                                    self.database_queue.put(new_feed_message)
                                    # write entries
                                    for entry in new_feed.entries:
                                        entry_message = DatabaseWriterMessage(DatabaseWriterMessage.ENTRY, entry)
                                        
                                            
                except Exception e:
                    feed.errors+=1
                    db_message = DatabaseWriterMessage(DatabaseWriterMessage.FEED, feed)
                    self.database_queue.put(db_message)
                
class DatabaseWriterMessage(object):
    """
    
    """
    FEED=0
    ENTRY=1
    def __init__(self, data_type, data):
        """
        """
        self.data_type = data_type
        self.data = data
                
class DatabaseWriter(threading.Thread):
    """
    
    """
    def __init__(self, database_engine, connection_string):
        """
        
        """
        super(DatabaseWriter, self).__init__(name=self.__class__.__name__)
        self.database = Interface(database_engine, connection_string)
        self.database_queue = Queue()
        self.stop_flag = stop_flag
        
    def run(self):
        """
        
        """
        while not self.stop_flag.is_set():
            message = self.database_queue.get()
            if message:
                if message.data_type==DatabaseWriterMessage.FEED:
                    self.database.update_feed(message.data)
                elif message.data_type==DatabaseWriterMessage.ENTRY:
                    self.database.add_entry(message.data)
    
    def stop(self):
        """
        
        """
        self.stop_flag.set()
                            
class FeedGrabManager(object):
    """
    
    """
    def __init__(self, threads, database_queue):
        """
        
        """
        self.threads = []
        self.feed_queue = Queue(maxsize=threads) # max size = number of threads means that there will never be any more in the queue than the threads can process
        self.database_queue = database_queue
        self.stop_flag = threading.Event()
        for i in range(threads):
            name = "FeedGrab-{0}".format(i)
            thread = FeedGrab(self.feed_queue, self.database_queue, self.stop_flag)
            thread.name=name
            self.threads.append(thread)
            
        def start_threads(self):
            """
            
            """
            for thread in self.threads:
                thread.start()
            
        def stop_threads(self):
            """
            
            """
            self.stop_flag.set()
            
        def put_feed(self, feed):
            """
            
            """
            inserted = False
            while not inserted:
                try:
                    self.feed_queue.put(feed, True, 60)
                    inserted = True
                except Full:
                    pass

class ManageGrabber(object):
    """
    
    """
    def __init__(self):
        """
        
        """
        self.db_writer_thread = DatabaseWriter(settings.DATABASE_ENGINE, settings.DB_CONNECTION_STRING)
        db_queue = self.db_thread.db_writer_thread
        self.grab_manager = FeedGrabManager(settings.THREADS, db_queue)
        self.database = Interface(settings.DATABASE_ENGINE, settings.DB_CONNECTION_STRING)
        self.stop_flag = threading.Event()
        
    def _start(self):
        """
        
        """
        self.db_thread.start()
        self.grab_manager.start()
        
    def stop(self):
        """
        
        """
        self.db_thread.stop()
        self.grab_manager.stop()
        self.stop_flag.set()
        
    def start(self):
        """
        Grabs feeds from the database and puts them on the feed queue
        so they can be checked for updates.
        """
        while not self.stop_flag.is_set():
            for feed in self.database.get_all_feeds():
                self.grab_manager.put(feed)
        
if __name__ == "__main__":
    mg = ManageGrabber()
    try:
        print "Starting. Press Ctrl+C to exit"
        mg.start()
    except KeyboardInterrupt:
        print "Safe exiting."
    finally:
        mg.stop()

