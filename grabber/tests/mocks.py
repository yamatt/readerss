
from mockito import *
from datetime import datetime, timedelta

Feed = mock()
Feed.last_accessed = datetime.now() - timedelta(minutes=10)
Feed.minimum_wait = 5
Feed.from_url = lambda: Feed
Feed.errors=0
Feed.title="Mock Feed Title"
Feed.id="Mock Feed ID"
