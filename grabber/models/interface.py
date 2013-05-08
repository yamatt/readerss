from models.model import Feed, Entry

class DatabaseValidation(Exception):
    pass

class Interface(object):
    """
    Middle ware database interface layer.
    """
    def __init__(self, engine_name, connection_string):
        self.database = self.get_database(engine_name, connection_string)
        
    def get_database(self, engine_name, connection_string):
        """
        Sets up database object.
        :param engine_name: the name of the engine model
        :param connection_string: the values used to set up the database engine
        """
        pass
        
    def get_all_feeds(self):
        """
        Return all the feed items so that they can be checked for new entries.
        TODO: less memory intensive way of doing this.
        """
        return map(lambda feed: Feed(**feed), self.database.get_items("feed"))
        
    def get_feed(self, feed_id):
        """
        Returns a Feed object based upon feed_id. To get feed id from URL
        create a Feed object and take the hash from that.
        :param feed_id: the string id of the feed to retrieve.
        """
        return Feed(self.database.get_item("feeds", feed_id))
        
    def update_feed(self, feed, add_entries=False):
        """
        Allows you to add or update a feed object in the database.
        """
        self.database.add_item("feeds", feed)
        if add_enrties:
            for entry in feed.entries:
                self.add_entry(entry)
        
    def get_entry(self, entry_id):
        """
        Returns an Entry object that represents the entry in the
        database. To get entry_id from URL create an Entry object and
        take the hash from that.
        :param entry_id: the string id of the feed to retrieve.
        """
        return Entry.from_database(self.database.get_item("entries", entry_id))
        
    def add_entry(self, entry):
        """
        Adds Entry object to the database. Validates whether Feed entry
        came from exists.
        :param entry: Entry object.
        """
        if self.get_feed(entry.feed_id):
            # look for previous entries
            self.database.add_item("entries", entry)
            # new entries table
            # entry state table
        else:
            raise DatabaseValidation("Feed is not valid for entry.")
