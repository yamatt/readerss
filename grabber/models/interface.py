from models.model import Feed, Entry

class DatabaseValidation(Exception):
    pass

class Interface(object):
    """
    Middle ware database interface layer.
    """
    ENGINES_PATH="engines"
    def __init__(self, engine_name, connection_string):
        self.database = self.get_database(engine_name)
        self.connection = self.database(connection_string)
        
    def get_database(self, engine_name):
        """
        Sets up database object.
        :param engine_name: the name of the engine model
        :param connection_string: the values used to set up the database engine
        """
        database_name = ".".join([self.ENGINES_PATH, engine_name])
        database_module = __import__(database_name, globals(), locals(), ["DATABASE"])
        return getattr(database_module, "DATABASE") # engine assigned to DATABASE variable
        
    def get_all_feeds(self):
        """
        Return all the feed items so that they can be checked for new entries.
        TODO: less memory intensive way of doing this.
        """
        items = self.connection.get_items(Feed.TYPE)
        return map(lambda feed: Feed(**feed), items)
        
    def get_feed(self, feed_id):
        """
        Returns a Feed object based upon feed_id. To get feed id from URL
        create a Feed object and take the hash from that.
        :param feed_id: the string id of the feed to retrieve.
        """
        item = self.connection.get_item(Feed.TYPE, feed_id)
        return Feed(**item)
        
    def add_feed(self, feed):
        """
        Allows you to insert a feed item in the database.
        """
        self.update_feed(feed)
        
    def update_feed(self, feed, add_entries=False):
        """
        Allows you to add or update a feed object in the database.
        """
        self.connection.add_item(Feed.TYPE, feed.to_database())
        if add_entries:
            for entry in feed.entries:
                self.add_entry(entry)
        
    def get_entry(self, entry_id):
        """
        Returns an Entry object that represents the entry in the
        database. To get entry_id from URL create an Entry object and
        take the hash from that.
        :param entry_id: the string id of the feed to retrieve.
        """
        return Entry(**self.connection.get_item(Entry.TYPE, entry_id))
        
    def add_entry(self, entry):
        """
        Adds Entry object to the database. Validates whether Feed entry
        came from exists.
        :param entry: Entry object.
        """
        if self.get_feed(entry.feed_id):
            # look for previous entries
            self.connection.add_item(Entry.TYPE, entry.to_database())
            # new entries table for when a new entry is added
            # entry state table for marking them as unread
        else:
            raise DatabaseValidation("Feed is not valid for entry.")
            
    def add_entries(self, entries):
        if all(lambda entry: self.get_feed(entry.feed_id)):
            self.connection.add_items(entries[0].TYPE, map(lambda entry: entry.to_database(), entries))
        else:
            raise DatabaseValidation("Feed is not valid for entry.")
