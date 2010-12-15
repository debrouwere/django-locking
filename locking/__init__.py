from django.conf import settings
import logging
import urls

LOCK_TIMEOUT = getattr(settings, 'LOCK_TIMEOUT', 1800)

logger = logging.getLogger('django.locker')