import logging

DATABASE_ENGINE="Sqlalchemy"
DATABASE_CONNECTION_STRING="sqlite:///grabber.db"

MAX_ACCESS_WAIT=30 # minutes
MIN_ACCESS_WAIT=3 # minutes
THREADS=1

LOGGING_FORMAT="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOGGING_LEVEL=logging.INFO
