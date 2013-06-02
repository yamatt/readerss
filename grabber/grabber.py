#!/usr/bin/env python2
 
import threading
from threading import Event
from Queue import Queue, Full as QueueFull, Empty as QueueEmpty
from time import sleep
from datetime import timedelta

import logging

from robotsparser import RobotsTXTParser

from models.model import Feed, Entry
from models.interface import Interface

import settings

logging.basicConfig(
    level=settings.LOGGING_LEVEL,
    format=settings.LOGGING_FORMAT
)

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
            feed = None
            try:
                # arbritrary timeout to prevent total blocking and lack of exiting
                feed = self.feed_queue.get(timeout=3)
            except QueueEmpty:
                pass
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
                                    self.database_queue.put(new_feed)
                                    # write entries
                                    for entry in new_feed.entries:
                                        self.database_queue.put(entry)
                                        
                                            
                except Exception as e:
                    feed.errors+=1
                    self.database_queue.put(feed)
                
class DatabaseWriter(threading.Thread):
    """
    This handles database writes from the feed grabber.
    """
    def __init__(self, database_engine, connection_string, stop_flag):
        """
        Set up the connection to the database, the queues and writer
        thread.
        :param database_engine: the name of the engine to use.
        :param connection_string: the options for the database engine
        """
        super(DatabaseWriter, self).__init__(name=self.__class__.__name__)
        self.database = Interface(database_engine, connection_string)
        self.database_queue = Queue()
        self.stop_flag = stop_flag
        
    def run(self):
        """
        Writes messages in batches from the queue. It sleeps 3 seconds
        for messages to build up in the queue before writing so that a
        lot of  messages can be pulled out and written as a bulk write.
        We don't mind it being too lossy here because the at the next
        iteration anything missing will be pulled in again.
        """
        while not self.stop_flag.is_set():
            data = []
            while not self.database_queue.empty():
                result = self.database_queue.get_nowait()
                data.append(result)
            if len(data) > 0:
                logging.info("Writing {0} bits of information to the database".format(len(data)))
                for item in data:
                    if item.TYPE == Feed.TYPE:
                        self.database.update_feed(item)
                    elif item.TYPE == Entry.TYPE:
                        self.database.add_entry(item)
                
            # waits 3 seconds for the queue to be populated
            sleep(3)
    
    def stop(self):
        """
        Tells the thread to die.
        """
        self.stop_flag.set()
                            
class FeedGrabManager(object):
    """
    Handles the multiple feed grabber threads.
    """
    def __init__(self, threads_count, database_queue):
        """
        Sets up the feed grabber threads.
        :param threads:an integer for the number of threads to generate.
        :param database_queue:the queue object used to send items to be
        writen to the database.
        """
        self.threads = []
        self.feed_queue = Queue(maxsize=threads_count) # max size = number of threads means that there will never be any more in the queue than the threads can process
        self.database_queue = database_queue
        self.stop_flag = threading.Event()
        for i in range(threads_count):
            self.add_thread()
        logging.info("Started {0} feed threads".format(len(self.threads)))
        
    def add_thread(self):
        name = "FeedGrab-{0}".format(len(self.threads))
        thread = FeedGrab(self.feed_queue, self.database_queue, self.stop_flag)
        thread.name=name
        self.threads.append(thread)
            
    def start(self):
        """
        Start all threads.
        """
        for thread in self.threads:
            thread.start()
        
    def stop(self):
        """
        Set the flag to tell the threads to stop.
        """
        self.stop_flag.set()
        
    def put_feed(self, feed):
        """
        A shorthand function to put feeds on the queue. The queue
        used here is small so that it doesn't take up too much
        memory. It also guarentees that the feed will be put on the
        queue. This queue is kept populated with feed entries so
        that the threads keep looking for new items.
        :param feed: the feed to be processed.
        """
        inserted = False
        while not inserted:
            try:
                self.feed_queue.put(feed, True, 60)
                inserted = True
            except QueueFull:
                pass

class ManageGrabber(object):
    """
    Handles the integration of the entire process.
    """
    def __init__(self):
        """
        Sets up the database writer, necessary queues and the feed
        grabber manager.
        """
        self.stop_flag = threading.Event()
        self.db_writer_thread = DatabaseWriter(settings.DATABASE_ENGINE, settings.DB_CONNECTION_STRING, self.stop_flag)
        db_queue = self.db_writer_thread.database_queue
        self.grab_manager = FeedGrabManager(settings.THREADS, db_queue)
        self.database = Interface(settings.DATABASE_ENGINE, settings.DB_CONNECTION_STRING)
        
    def stop(self):
        """
        Stops the threads. Can only be called once start has exited.
        """
        self.db_writer_thread.stop()
        self.grab_manager.stop()
        self.stop_flag.set()
        
    def start(self):
        """
        Starts the threads off then grabs feeds from the database and
        puts them on the feed queue so they can be checked for updates.
        """
        self.db_writer_thread.start()
        self.grab_manager.start()
        logging.info("Started threads. Starting feed processors.")
        while not self.stop_flag.is_set():
            for feed in self.database.get_all_feeds():
                self.grab_manager.put_feed(feed)
        
if __name__ == "__main__":
    mg = ManageGrabber()
    try:
        print "Starting. Press Ctrl+C to exit"
        mg.start()
    except KeyboardInterrupt:
        print "Safe exiting."
    finally:
        mg.stop()

