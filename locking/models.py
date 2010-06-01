# encoding: utf-8

from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth import models as auth

from locking import LOCK_TIMEOUT, logging

class LockableModel(models.Model):
    class Meta:
        abstract = True
        
    # voorzieningen die concurrent editing onmogelijk maken
    locked_at = models.DateTimeField(null=True, editable=False)
    locked_by = models.ForeignKey(auth.User, related_name="working_on_%(class)s", null=True, editable=False)

    @property
    def is_locked(self):
        """
        docstring todo
        """
        if isinstance(self.locked_at, datetime):
            # artikels worden een half uur gesloten
            if (datetime.today() - self.locked_at).seconds < LOCK_TIMEOUT:
                return True
            else:
                return False
        return False
    
    @property
    def lock_seconds_remaining(self):
        """
        docstring todo
        """
        return LOCK_TIMEOUT - (datetime.today() - self.locked_at).seconds
    
    """
    test
    """
    def lock_for(self, user=False, hard_lock=False):
        """
        docstring todo
        """
        logging.info("Attempting to initiate a lock for user `%s`" % user)
    
        # the save method unlocks the object, but of course
        # it should keep things nicely locked when we're only
        # saving to apply the lock!
        self._initiate_lock = True
        
        # False opens up the lock, a valid user closes it.
        # I'm not too happy with this as the API, and will probably refactor this.
        if isinstance(user, auth.User):
            self.locked_at = datetime.today()
            self.locked_by = user
            logging.info("Initiated a lock for `%s` at %s" % (self.locked_by, self.locked_at))
        elif user is False:
            logging.info("Freed lock on `%s`" % self)
            # Eh, somewhat shoddy as far as exception handling goes. Should clean this up.
            try:
                self.locked_at = self.locked_by = None
            except:
                pass
    
    def unlock_for(self, user):
        """
        docstring todo
        """
        logging.info("Attempting to open up a lock on `%s` by user `%s`" % (self, user))
    
        # refactor: should raise exceptions instead
        if self.is_locked_by(user):
            self.unlock()
            return True
        else:
            return False
    
    def unlock(self):
        """
        docstring todo
        """
        # TO FIX: this obviously won't work.
        self.lock_for(False)
    
    def lock_applies_to(self, user):
        """
        docstring todo
        """
        logging.info("Checking if the lock on `%s` applies to user `%s`" % (self, user))
        # a lock does not apply to the person who initiated the lock
        if self.is_locked and self.locked_by != user:
            logging.info("Lock applies.")
            return True
        else:
            logging.info("Lock does not apply.")
            return False
    
    def is_locked_by(self, user):
        """
        docstring todo
        """
        return user == self.locked_by
    
    def save(self, *vargs, **kwargs):
        # see _set_lock: we don't disengage the lock if the 
        # entire point of this save is to engage the lock           
        if getattr(self, '_initiate_lock', False) is False:
            logging.info("Saving `%s` and disengaging any existing lock, if necessary." % self)
            self.unlock()
        
        super(LockableModel, self).save(*vargs, **kwargs)