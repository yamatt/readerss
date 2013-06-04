from urlparse import urljoin, urlparse
import urllib2
import re
from fnmatch import fnmatch
from datetime import timedelta

class RobotsTXTParser(object):
    ROBOTSTXT_PATH="/robots.txt"
    
    USER_AGENT_MATCH=re.compile(r"^User-agent: *(?P<str>\w*).*$")
    ALLOW_MATCH=re.compile(r"^Allow: *(?P<str>\w*).*$")
    DISALLOW_MATCH=re.compile(r"^Disallow: *(?P<str>\w*).*$")
    CRAWL_DELAY_MATCH=re.compile(r"^Crawl-delay: *(?P<str>\w*).*$")
    
    def __init__(self, contents, user_agent=""):
        self.user_agent = user_agent
        self.contents = contents
        
    @classmethod
    def from_url(cls, url, user_agent=""):
        """
        Create RTXTP object from url.
        :param url: URL for server you wish to request the robots.txt
            for. E.g.: http://example.com/foo/bar.html
        """
        url = urljoin(url, RobotsTXTParser.ROBOTSTXT_PATH)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        return cls.from_file(response, user_agent)
        
    @classmethod
    def from_file(cls, f, user_agent=""):
        """
        Create RTXTP object from file object.
        :param f: String path to file. E.g.:/tmp/foo.txt
        """
        return cls(f.read(), user_agent)
        
    def user_agent_match(self, user_agent):
        """
        Detect if the user agent is the one that applies to this tool.
        """
        user_agent = user_agent.strip()
        if user_agent == "" or user_agent == "*":
            return True
        elif user_agent == self.user_agent:
            return True
        return False
        
    def get_crawl_delay(self):
        """
        If successful returns timedelta object for how long the minimum
        wait should be before the server is tried again since the last
        try. If unsuccessful returns None object.
        """
        current_agent=""
        for l in self.contents.split():
            if self.USER_AGENT_MATCH.match(l):
                m = self.USER_AGENT_MATCH.match(l)
                current_agent = m.groupdict().get("str", "")
            elif self.CRAWL_DELAY_MATCH.match(l) and self.user_agent_match(current_agent):
                m = self.CRAWL_DELAY_MATCH.match(l)
                value = m.groupdict().get("str", "0")
                if value.isdigit():
                    return timedelta(seconds=int(value))
                    
    def url_acceptable(self, url, strict=False):
        """
        A simple helper function to strip the path part of the url and
        return you if that path is acceptable. Is useful if you don't
        want to do the path stripping yourself.
        :param url: the url to check. E.g.: http://example.com/foo/bar.txt
        :param strict: if true will return None (false) if it is unknown
            whether the path can be accessed. If false and is unknown
            it is assumed the path can be accessed.
        """
        return self.path_acceptable(urlparse(url).path)
        
    def path_acceptable(self, path, strict=False):
        """
        Returns a true value if the path supplied is allowed access by
        the robots.txt file. Returns a false value if it cannot be
        accessed and a None if it is unknown (which can be interpreted
        as True).
        :param path: the absolute path to check. E.g.: /foo/bar.txt
        :param strict: if true will return None (false) if it is unknown
            whether the path can be accessed. If false and is unknown
            it is assumed the path can be accessed.
        """
        current_agent=""
        for l in self.contents.split():
            if self.USER_AGENT_MATCH.match(l):
                m = self.USER_AGENT_MATCH.match(l)
                current_agent = m.groupdict().get("str", "")
            elif self.DISALLOW_MATCH.match(l) and self.user_agent_match(current_agent):
                m = self.DISALLOW_MATCH.match(l)
                pattern = m.groupdict().get("str", "")
                if fnmatch(path, pattern):
                    return False
            elif self.ALLOW_MATCH.match(l) and self.user_agent_match(current_agent):
                m = self.ALLOW_MATCH.match(l)
                pattern = m.groupdict().get("str", "")
                if fnmatch(path, pattern):
                    return True
        if not strict:
            return True
    
                
