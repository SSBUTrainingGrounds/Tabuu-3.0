import logging
from logging.handlers import TimedRotatingFileHandler

def create_logger():
    path = r"./logs/tabuu3.log"
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)

    handler = TimedRotatingFileHandler(filename=path, when="midnight", backupCount=7, encoding='utf-8')
    handler.suffix = "%Y%m%d"
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

    logger.addHandler(handler)

def get_logger():
    return logging.getLogger('discord')