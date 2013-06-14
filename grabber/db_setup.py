#!/usr/bin/env python2
from models.interface import Interface
import settings

db = Interface(settings.DATABASE_ENGINE, settings.DATABASE_CONNECTION_STRING)

def build_tables():
    db.connection.setup_database()
    
if __name__ == "__main__":
    build_tables()
