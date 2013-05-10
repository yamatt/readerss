import feedparser # needs to be from git repo
from hashlib import sha256
from time import mktime
from datetime import datetime, timedelta
import settings

def hasher(v):
    return sha256(v).hexdigest()

class Feed(object):
    """
    Represents a RSS/Atom feed.
    """
    TYPE="feed"
    @classmethod
    def from_url(cls, url):
        """
        Creates this feed object from a given url.
        :param url: url for RSS/Atom feed.
        """
        feed = feedparser.parse(url).feed
        return cls(
            url=url,
            title=feed.title,
            subtitle=feed.subtitle,
            updated=datetime.fromtimestamp(mktime(feed.updated_parsed)),
            published=datetime.fromtimestamp(mktime(feed.published_parsed)),
            link=feed.link
        )
        
    def __init__(self, **feed):
        """
        Creates the Feed object from raw data.
        :param feed:a dictionary of possible feed items.
        """
        self.id = feed.get("id")
        self.url = feed.get("url")
        self.title = feed.get("title")
        self.subtitle = feed.get("subtitle")
        self.updated = feed.get("updated")
        self.published = feed.get("published")
        self.link = feed.get("link")
        self.last_accessed = feed.get("last_accessed")
        self.minimum_wait = feed.get("minimum_wait", settings.MIN_ACCESS_WAIT)
        self.errors = feed.get("error", 0)
        
        self.entries = map(lambda entry: Entry(
            feed_id=self.hashed_id,
            title=entry.title,
            summary=entry.summary,
            link=entry.link,
            updated=datetime.fromtimestamp(mktime(entry.updated_parsed)),
            published=datetime.fromtimestamp(mktime(entry.published_parsed)),
        ), feed.get("entries", []))
        
    def to_database(self):
        """
        Returns database representation of object.
        """
        d = self.__dict__
        d['id'] = hasher(d['url'])
        return d
        
class Entry(object):
    """
    Represents a RSS/Atom feed item.
    """
    TYPE="feed"
    @staticmethod
    def to_id(**entry):
        """
        Generates the unique id for this item based upon it's attributes.
        :param entry:a dictionary of entry items.
        """
        if entry.guidislink:
            return entry.get("link")
        else:
            if entry.get("id"):
                return entry["id"]
            else:
                return "{0}{1}".format(entry.get("title"), entry.get("published"))
                
    def __init__(self, **entry):
        """
        Creates the entry from raw data.
        :param entry:a dictionary of possible entry items.
        """
        self.id = hasher(self.to_id(**entry))
        self.feed_id = entry.get("feed_id") 
        self.title=entry.get("title")
        self.summary=entry.get("summary")
        self.link=entry.get("link")
        self.updated=entry.get("updated")
        self.published=entry.get("published")
        
    def __eq__(self, other):
        """
        Allows two entries to be compared.
        :param other:other entry item to be compared to.
        """
        return (self.id == other.id)
        
    def to_database(self):
        """
        Returns database representation of object.
        """
        d = self.__dict__
        d['id'] = hasher(self.to_id(self))
        return d
