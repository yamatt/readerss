from hashlib import sha256
from time import mktime
from datetime import datetime, timedelta
import settings

try:
    import feedparser # needs to be from git repo (https://code.google.com/p/feedparser/)
except ImportError as e:
    import imp
    try:
        feedparser = imp.load_source("feedparser", "feedparser_git/feedparser/feedparser.py")
    except ImportError as e:
        raise RuntimeError("No feedparser module found. Please install one or use git submodule update --init to clone the sub modules")
        
def hasher(v):
    return sha256(v.encode("utf-8")).hexdigest()

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
        fp = feedparser.parse(url)
        feed = fp.get("feed")
        entries = fp.get("entries", [])
        updated = feed.get("updated_parsed")
        if updated:
            updated = datetime.fromtimestamp(mktime(feed.updated_parsed))
        published = feed.get("feed.published_parsed")
        if published:
            published=datetime.fromtimestamp(mktime(feed.published_parsed))
        return cls(
            url=url,
            title=feed.title,
            subtitle=feed.subtitle,
            updated=updated,
            published=published,
            link=feed.link,
            entries=entries
        )
        
    def __init__(self, **feed):
        """
        Creates the Feed object from raw data.
        :param feed:a dictionary of possible feed items.
        """
        self.url = feed.get("url")
        self.id = hasher(self.url)
        self.title = feed.get("title")
        self.subtitle = feed.get("subtitle")
        self.updated = feed.get("updated")
        self.published = feed.get("published")
        self.link = feed.get("link")
        self.last_accessed = feed.get("last_accessed")
        self.minimum_wait = feed.get("minimum_wait", settings.MIN_ACCESS_WAIT)
        self.errors = feed.get("error", 0)
        
        self.entries = []
        for entry in feed.get("entries", []):
            updated = None
            if hasattr(entry, "updated_parsed"):
                updated=datetime.fromtimestamp(mktime(entry.updated_parsed))
            published = None
            if hasattr(entry, "published_parsed"):
                published=datetime.fromtimestamp(mktime(entry.published_parsed))
            parsed_entry = Entry(
                feed_id=self.id,
                title=entry.title,
                summary=entry.summary,
                link=entry.link,
                updated=updated,
                published=published,
            )
            self.entries.append(parsed_entry)
        
    def can_check(self):
        if not self.last_accessed:
            return True
        else:
            next_access = self.last_accessed + timedelta(minutes=self.minimum_wait)
            if datetime.now() > next_access:
                return True
                
        
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
    TYPE="entry"
    @staticmethod
    def to_id(**entry):
        """
        Generates the unique id for this item based upon it's attributes.
        :param entry:a dictionary of entry items.
        """
        if entry.get("guidislink") and entry.get("link"):
            # guid value?
            return "".join([entry.get("link"), entry.get("feed_id")])
        else:
            if entry.get("published"):
                return "".join([entry.get("title"), entry.get("published").isoformat(), entry.get("feed_id")])
            else:
                return "".join([entry.get("title"), entry.get("feed_id")])
                
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
        
    def compare_source(self, other):
        """
        Used like eq to compare if the entries also came from the same source
        """
        return self.__eq__(other) and self.feed_id == other.feed_id
        
    def to_database(self):
        """
        Returns database representation of object.
        """
        d = self.__dict__
        d['id'] = hasher(self.to_id(**d))
        return d
