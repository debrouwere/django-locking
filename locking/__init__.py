from django.conf import settings
import logging

LOCK_TIMEOUT = getattr(settings, 'LOCK_TIMEOUT', 1800)

logger = logging.getLogger('django.locker')