==============
The public API
==============

Some examples
-------------

.. highlight:: python

Let's import some models and fixtures to play around with.

    >>> from locking.tests.models import Story
    >>> from django.contrib.auth.models import User
    >>> user = User.objects.all()[0]
    >>> story = Story.objects.all()[0]

Let's lock a story.

    >>> story.lock_for(user)
    INFO:root:Attempting to initiate a lock for user `stdbrouw`
    INFO:root:Initiated a lock for `stdbrouw` at 2010-06-01 09:33:46.540376
    # We can access all kind of information about the lock
    >>> story.locked_at
    datetime.datetime(2010, 6, 1, 9, 38, 3, 101238)
    >>> story.locked_by
    <User: stdbrouw>
    >>> story.is_locked
    True
    >>> story.lock_seconds_remaining
    1767
    # Remember: a lock isn't actually active until we save it to the database!
    >>> story.save()
    
And we can unlock again. Although it's possible to force an unlock, it's better to unlock specifically for the user that locked the content in the first place -- that way django-locking can protest if the wrong user tries to unlock something.

    >>> story.unlock_for(user)
    INFO:root:Attempting to open up a lock on `Story object` by user `blub`
    INFO:root:Attempting to initiate a lock for user `False`
    INFO:root:Freed lock on `Story object`
    True
    >>> story.save()

Additionally, the LockableModel class defines three `managers <http://docs.djangoproject.com/en/dev/topics/db/managers/>`_: ``objects``, ``locked`` and ``unlocked``, that unsurprisingly give you access to, respectively, all objects, locked objects and unlocked objects.

Methods and attributes
----------------------

Most functionality and domain logic of ``django-locking`` resides in the ``LockableModel``, with the views providing little more than an interface to the web.

.. automodule:: locking.models
   :show-inheritance:
   :members:
   :undoc-members:

Nomenclature
------------

``django-locking`` tries to be consistent in its terminology, even if it doesn't always succeed. An object can be **locked** and **unlocked**, in which case we've **disengaged** a lock. A lock can **apply** to a certain user, or not apply because it was **initiated** by that same user. A lock will **expire** once it has been in place longer than a predefined **timeout**.