import sys
import logging
from django.conf import settings

LOCK_TIMEOUT = getattr(settings, 'LOCK_TIMEOUT', 1800)
LOCKING_LOG_LEVEL = getattr(settings, 'LOCKING_LOG_LEVEL', logging.INFO)
FORMAT = "[locking] [%(levelname)s] %(message)s"
LOCKING_DEFAULT_LOGGER_NAME = 'stdbrouw.django-locking'
LOCKING_LOGGER_NAME = getattr(settings, 'LOCKING_LOGGER_NAME', LOCKING_DEFAULT_LOGGER_NAME)

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

if not hasattr(logging, 'LOCKING_LOGGER'):
    logging.LOCKING_LOGGER = False

if not logging.LOCKING_LOGGER:
    logger = logging.getLogger(LOCKING_LOGGER_NAME)
    if LOCKING_LOGGER_NAME == LOCKING_DEFAULT_LOGGER_NAME:
        ch = logging.StreamHandler()
        formatter = logging.Formatter(FORMAT)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    else:
        nh = NullHandler()
        logger.addHandler(nh)
    logger.setLevel(LOCKING_LOG_LEVEL)
    logging.LOCKING_LOGGER = True