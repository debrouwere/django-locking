# encoding: utf-8

from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth import models as auth

from locking import LOCK_TIMEOUT, logger
import managers

class ObjectLockedError(IOError):
    pass

class LockableModel(models.Model):
    """ LockableModel comes with three managers: ``objects``, ``locked`` and 
    ``unlocked``. They do what you'd expect them to. """

    objects = managers.Manager()
    locked = managers.LockedManager()
    unlocked = managers.UnlockedManager()

    def __init__(self, *vargs, **kwargs):
        super(LockableModel, self).__init__(*vargs, **kwargs)
        self._state.locking = False

    class Meta:
        abstract = True
        
    _locked_at = models.DateTimeField(db_column='locked_at', 
        null=True,
        editable=False)
    _locked_by = models.ForeignKey(auth.User, 
        db_column='locked_by',
        related_name="working_on_%(class)s",
        null=True,
        editable=False)
    _hard_lock = models.BooleanField(db_column='hard_lock', default=False, editable=False)
    
    # We don't want end-developers to manipulate database fields directly, 
    # hence we're putting these behind simple getters.
    # End-developers should use functionality like the lock_for method instead.
    @property
    def locked_at(self):
        """A simple ``DateTimeField`` that is the heart of the locking mechanism. Read-only."""
        return self._locked_at
    
    @property
    def locked_by(self):
        """``locked_by`` is a foreign key to ``auth.User``. The ``related_name`` on the 
        User object is ``working_on_%(class)s``. Read-only."""
        return self._locked_by
    
    @property
    def lock_type(self):
        """ Returns the type of lock that is currently active. Either
        ``hard``, ``soft`` or ``None``. Read-only. """
        if self.is_locked:
            if self._hard_lock:
                return "hard"
            else:
                return "soft"
        else:
            return None

    @property
    def is_locked(self):
        """
        A read-only property that returns True or False.
        Works by calculating if the last lock (self.locked_at) has timed out or not.
        """
        if isinstance(self.locked_at, datetime):
            if (datetime.today() - self.locked_at).seconds < LOCK_TIMEOUT:
                return True
            else:
                return False
        return False
    
    @property
    def lock_seconds_remaining(self):
        """
        A read-only property that returns the amount of seconds remaining before
        any existing lock times out.
        
        May or may not return a negative number if the object is currently unlocked.
        That number represents the amount of seconds since the last lock expired.
        
        If you want to extend a lock beyond its current expiry date, initiate a new
        lock using the ``lock_for`` method.
        """
        return LOCK_TIMEOUT - (datetime.today() - self.locked_at).seconds
    
    def lock_for(self, user, hard_lock=False):
        """
        Together with ``unlock_for`` this is probably the most important method 
        on this model. If applicable to your use-case, you should lock for a specific 
        user; that way, we can throw an exception when another user tries to unlock
        an object they haven't locked themselves.
        
        When using soft locks (the default), any process can still use the save method
        on this object. If you set ``hard_lock=True``, trying to save an object
        without first unlocking will raise an ``ObjectLockedError``.
        
        Don't use hard locks unless you really need them. See :doc:`design`.
        """
        logger.info("Attempting to initiate a lock for user `%s`" % user)

        if not isinstance(user, auth.User):
            raise ValueError("You should pass a valid auth.User to lock_for.")
        
        if self.lock_applies_to(user):
            raise ObjectLockedError("This object is already locked by another user. \
                May not override, except through the `unlock` method.")
        else:
            self._locked_at = datetime.today()
            self._locked_by = user
            self._hard_lock = self.__init_hard_lock = hard_lock
            date = self.locked_at.strftime("%H:%M:%S")
            # an administrative toggle, to make it easier for devs to extend `django-locking`
            # and react to locking and unlocking
            self._state.locking = True
            logger.info("Initiated a %s lock for `%s` at %s" % (self.lock_type, self.locked_by, self.locked_at))     

    def unlock(self):
        """
        This method serves solely to allow the application itself or admin users
        to do manual lock overrides, even if they haven't initiated these
        locks themselves. Otherwise, use ``unlock_for``.
        """
        self._locked_at = self._locked_by = None
        # an administrative toggle, to make it easier for devs to extend `django-locking`
        # and react to locking and unlocking
        self._state.locking = True
        logger.info("Disengaged lock on `%s`" % self)
    
    def unlock_for(self, user):
        """
        See ``lock_for``. If the lock was initiated for a specific user, 
        unlocking will fail unless that same user requested the unlocking. 
        Manual overrides should use the ``unlock`` method instead.
        
        Will raise a ObjectLockedError exception when the current user isn't authorized to
        unlock the object.
        """
        logger.info("Attempting to open up a lock on `%s` by user `%s`" % (self, user))
    
        # refactor: should raise exceptions instead
        if self.is_locked_by(user):
            self.unlock()
        else:
            raise ObjectLockedError("Trying to unlock for another user than the one who initiated the currently active lock. This is not allowed. You may want to try a manual override through the `unlock` method instead.")
    
    def lock_applies_to(self, user):
        """
        A lock does not apply to the user who initiated the lock. Thus, 
        ``lock_applies_to`` is used to ascertain whether a user is allowed
        to edit a locked object.
        """
        logger.info("Checking if the lock on `%s` applies to user `%s`" % (self, user))
        # a lock does not apply to the person who initiated the lock
        if self.is_locked and self.locked_by != user:
            logger.info("Lock applies.")
            return True
        else:
            logger.info("Lock does not apply.")
            return False
    
    def is_locked_by(self, user):
        """
        Returns True or False. Can be used to test whether this object is locked by
        a certain user. The ``lock_applies_to`` method and the ``is_locked`` and 
        ``locked_by`` attributes are probably more useful for most intents and
        purposes.
        """
        return user == self.locked_by
    
    def save(self, *vargs, **kwargs):
        if self.lock_type == 'hard' and not self.__init_hard_lock:
            raise ObjectLockedError("""There is currently a hard lock in place. You may not save.
            If you're requesting this save in order to unlock this object for the user who
            initiated the lock, make sure to call `unlock_for` first, with the user as
            the argument.""")
        self.__init_hard_lock = False
        
        super(LockableModel, self).save(*vargs, **kwargs)
        self._state.locking = False