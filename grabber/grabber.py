#!/usr/bin/env python2
 
import threading
from threading import Event
from Queue import Queue, Full as QueueFull, Empty as QueueEmpty
from time import sleep
from datetime import timedelta, datetime

import logging

from robotsparser import RobotsTXTParser

from models.model import Feed, Entry
from models.interface import Interface

import settings

logging.basicConfig(
    level=settings.LOGGING_LEVEL,
    format=settings.LOGGING_FORMAT
)

class FeedGrab(threading.Thread):
    """
    Processes feeds to grab new entries from them.
    """
    def __init__(self, feed_queue, database_engine, connection_string, stop_flag):
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
        self.database = Interface(database_engine, connection_string)
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
            try:
                # arbritrary timeout to prevent total blocking and lack of exiting
                feed_id = self.feed_queue.get(timeout=3)
                if feed_id:
                    feed = self.database.get_feed(feed_id)
                    self.add_latest(feed)
            except QueueEmpty:
                pass
    
    def add_latest(self, feed):
        # worth checking yet?
        now = datetime.now()
        if feed.can_check():
            new_feed = Feed.from_url(feed.url)
            new_feed.last_accessed = now
            new_feed.errors = feed.errors
            # write feed
            self.database.update_feed(new_feed)
            # write entries
            # just send the entries to the database.rather than faffing around determining if it has been updated or not
            # TODO: detect duplicate ids and create a new separate entry
            for entry in new_feed.entries:
                self.database.add_entry(entry)
                            
class FeedGrabManager(object):
    """
    Handles the multiple feed grabber threads.
    """
    def __init__(self, threads_count):
        """
        Sets up the feed grabber threads.
        :param threads:an integer for the number of threads to generate.
        :param database_queue:the queue object used to send items to be
        writen to the database.
        """
        self.threads = []
        self.feed_queue = Queue(maxsize=threads_count) # max size = number of threads means that there will never be any more in the queue than the threads can process
        self.stop_flag = threading.Event()
        for i in range(threads_count):
            self.add_thread()
        logging.info("Started {0} feed threads".format(len(self.threads)))
        
    def add_thread(self):
        name = "FeedGrab-{0}".format(len(self.threads))
        thread = FeedGrab(self.feed_queue, settings.DATABASE_ENGINE, settings.DATABASE_CONNECTION_STRING, self.stop_flag)
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
        self.grab_manager = FeedGrabManager(settings.THREADS)
        self.database = Interface(settings.DATABASE_ENGINE, settings.DATABASE_CONNECTION_STRING)
        
    def stop(self):
        """
        Stops the threads. Can only be called once start has exited.
        """
        self.grab_manager.stop()
        self.stop_flag.set()
        
    def run(self):
        """
        Starts the threads off then grabs feeds from the database and
        puts them on the feed queue so they can be checked for updates.
        """
        self.grab_manager.start()
        logging.info("Started threads. Starting feed processors.")
        for feed in self.database.get_all_feeds():
            self.grab_manager.put_feed(feed.id)
        
if __name__ == "__main__":
    mg = ManageGrabber()
    try:
        print "Starting. Press Ctrl+C to exit"
        mg.run()
    except KeyboardInterrupt:
        print "Safe exiting."
    except Exception as e:
        logging.error("An error caused an exit: {0}".format(e))
    finally:
        mg.stop()

